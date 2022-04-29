import asyncio
from factory import models, oauth2, utils
from factory.config import settings
from factory.database import get_db
from factory.schema import token_schema, stream_schema
from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session
from .connection_manager import con_manager
from sqlalchemy import desc, func
from websockets.exceptions import ConnectionClosedError

stream_router = APIRouter(prefix="/stream")


@stream_router.get(
    "/check",
    description="check new order name in transcations.",
    response_model=str,
)
def check_order_count(
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(
        oauth2.get_listener,
    ),
):
    data = (
        db.query(func.count(models.Transcation.id))
        .filter(models.Transcation.transcation_type != utils.TransType.update)
        .all()
    )
    # as it returns as a tuple.[(x,)]
    return data[0][0]


@stream_router.get(
    "/check/{id}",
    response_model=stream_schema.CheckOrderByIdResponse,
)
def get_order_from_trans(
    id: int,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_listener),
):
    data: models.Transcation = db.query(models.Transcation).get(id)
    return data


## even tho we wrote prefix for stream router as '/stream' at the top, we need to add here again as WEBSOCKET DOES NOT RECOGNIZE THE PREFIX FROM APIROUTER CLASS.
@stream_router.websocket("/stream/listen")
async def stream_all_new_order(
    websoc: WebSocket,
    db: Session = Depends(get_db),
    # manager_info: token_schema.PayloadData = Depends(oauth2.get_listener),
):
    await con_manager.connect(websocket=websoc)
    print(con_manager.active_connections)
    try:
        while True:
            result = (
                db.query(
                    models.Transcation.product_type,
                    func.count(models.Transcation.id).label("count"),
                )
                .group_by(models.Transcation.product_type)
                .filter(
                    models.Transcation.production_stage != utils.ProductionStage.done
                )
                .all()
            )
            print(result)

            # total_insert_order_for_each = (
            #     db.query(
            #         models.Transcation.product_type,
            #         func.count(models.Transcation.id).label("count"),
            #     )
            #     .group_by(models.Transcation.product_type)
            #     .filter(models.Transcation.transcation_type == utils.TransType.insert)
            #     .all()
            # )
            # total_delete_order_for_each = (
            #     db.query(
            #         models.Transcation.product_type,
            #         func.count(models.Transcation.id).label("count"),
            #     )
            #     .group_by(models.Transcation.product_type)
            #     .filter(models.Transcation.transcation_type == utils.TransType.delete)
            #     .all()
            # )

            # total_insert_list = [
            #     stream_schema.OrderCount.from_orm(i)
            #     for i in total_insert_order_for_each
            # ]
            # total_delete_list = [
            #     stream_schema.OrderCount.from_orm(i)
            #     for i in total_delete_order_for_each
            # ]
            final_result = [stream_schema.OrderCount.from_orm(i).dict() for i in result]

            await con_manager.broadcast(final_result)

            await asyncio.sleep(settings.stream_delay_time)
    except ConnectionClosedError:
        con_manager.disconnect(websoc)
