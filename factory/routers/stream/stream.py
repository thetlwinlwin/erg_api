import asyncio

from factory import models, oauth2, utils
from factory.config import settings
from factory.database import get_db
from factory.schema import stream_schema, token_schema
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import func
from sqlalchemy.orm import Session

from .connection_manager import con_manager

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


## INSERT_WITHOUT_DONE - DEL - UPDATE_WITH_DONE = CURRENT NON-DONE NUMBER OF ORDERS
## even tho we wrote prefix for stream router as '/stream' at the top, we need to add here again as WEBSOCKET DOES NOT RECOGNIZE THE PREFIX FROM APIROUTER CLASS.
@stream_router.websocket("/stream/listen")
async def stream_all_new_order(
    websoc: WebSocket,
    db: Session = Depends(get_db),
    # manager_info: token_schema.PayloadData = Depends(oauth2.get_listener),
):
    await con_manager.connect(websocket=websoc)
    try:
        while len(con_manager.active_connections) > 0:
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
            # total_insert_trans = (
            #     db.query(
            #         models.Transcation.product_type,
            #         func.count(models.Transcation.id).label("count"),
            #     )
            #     .group_by(models.Transcation.product_type)
            #     .filter_by(
            #         models.Transcation.transcation_type == utils.TransType.insert,
            #         models.Transcation.product_type != utils.ProductionStage.done,
            #     )
            #     .all()
            # )
            # total_delete_trans = (
            #     db.query(
            #         models.Transcation.product_type,
            #         func.count(models.Transcation.id).label("count"),
            #     )
            #     .group_by(models.Transcation.product_type)
            #     .filter(models.Transcation.transcation_type == utils.TransType.delete)
            #     .all()
            # )
            # total_updated_trans = (
            #     db.query(
            #         models.Transcation.product_type,
            #         func.count(models.Transcation.id).label("count"),
            #     )
            #     .group_by(models.Transcation.product_type)
            #     .filter_by(
            #         models.Transcation.transcation_type == utils.TransType.update,
            #         models.Transcation.production_stage == utils.ProductionStage.done,
            #     )
            #     .all()
            # )

            # total_inserts = [
            #     stream_schema.OrderCount.from_orm(i) for i in total_insert_trans
            # ]
            # total_deletes = [
            #     stream_schema.OrderCount.from_orm(i) for i in total_delete_trans
            # ]
            # total_updates = [
            #     stream_schema.OrderCount.from_orm(i) for i in total_updated_trans
            # ]

            final_result = [stream_schema.OrderCount.from_orm(i).dict() for i in result]

            await con_manager.broadcast(final_result)
            await asyncio.sleep(settings.stream_delay_time)
    except WebSocketDisconnect:
        con_manager.disconnect(websoc)
