from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Request,
    Response,
)
import asyncio
from sqlalchemy.orm import Session
from factory import models, oauth2
from factory.config import settings
from factory.database import get_db
from factory.schema import token_schema, ds_schema, orders_update_schema
from sqlalchemy import exc, func, desc
from .ds_con_manager import ds_con_manager
from factory.utils import Product, ProductionStage

ds_orders_router = APIRouter(
    prefix="/ds",
    tags=["Deck Sheet"],
)


@ds_orders_router.get(
    "/orders/all",
    description="The data is sorted by pick_up_time by default.",
    response_model=list[ds_schema.DSOrderOut],
)
def get_all_orders(
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    results = (
        db.query(models.DSOrder)
        .join(models.DSOrderDetails)
        .order_by(models.DSOrderDetails.pick_up_time.asc())
        .filter(models.DSOrderDetails.production_stage != ProductionStage.done)
    ).all()
    return results


@ds_orders_router.get(
    "/orders/search/customer_info",
    description="Search orders by customer info. Output will be sorted with most recent pick_up_time",
    response_model=list[ds_schema.DSOrderOut],
)
def search_order(
    request: Request,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    try:
        query_params = request.query_params._dict
        results_query = (
            db.query(models.DSOrder)
            .join(models.DSOrderDetails)
            .order_by(models.DSOrderDetails.pick_up_time.asc())
            .filter(models.DSOrderDetails.production_stage != ProductionStage.done)
            .join(models.Customer)
            .filter_by(**query_params)
        )

        return results_query.all()
    except exc.InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invaild Search Query. Check the parameters again.",
        )


@ds_orders_router.post("/create")
def create_an_order(
    order: ds_schema.DSOrderCreate,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    new_order = models.DSOrder(
        manager_id=manager_info.manager_id, customer_id=order.customer_id
    )
    new_order.ds_order_detail = models.DSOrderDetails(**order.ds_order_detail.dict())

    db.add(new_order)
    db.commit()


@ds_orders_router.put("/orders/details/update/{id}")
def update_an_order(
    id: int,
    order: orders_update_schema.OrderDetailUpdate,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_listener),
):
    order_query = db.query(models.DSOrderDetails).filter(models.DSOrderDetails.id == id)
    if order_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connect to the Admin.",
        )
    order_query.update(order.dict(), synchronize_session=False)
    db.commit()
    return


@ds_orders_router.delete(
    "/orders/delete/{id}",
    description="delete the existing order",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_an_order(
    id: int,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    order_to_delete: models.DSOrder = (
        db.query(models.DSOrder).filter(models.DSOrder.id == id).first()
    )
    if order_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order does not exist.",
        )
    # use this method to catch order object to be deleted in event listener (before_delete).
    if order_to_delete.ds_order_detail.production_stage == ProductionStage.pending:
        db.delete(order_to_delete)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The order is either done or producing and it cannot be stopped.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# # TODO: this has to change to stream location.
# ## ws:/localhost:8000/ds/listen will give error as websocket does not recognize the prefix from apirouter class.
# @ds_orders_router.websocket("/listen")
# async def ds_endpoint(
#     websocket: WebSocket,
#     # manager_info: token_schema.PayloadData = Depends(oauth2.get_manager),
#     db: Session = Depends(get_db),
# ):
#     await ds_con_manager.connect(websocket=websocket)
#     query = db.query(models.Transcation.id)
#     previous_count = query.count()
#     try:
#         while True:
#             await asyncio.sleep(settings.stream_delay_time)
#             current_count = query.count()
#             print(f"current_count is {current_count}")
#             if current_count != previous_count:
#                 data = (
#                     db.query(models.Transcation)
#                     .with_entities(
#                         models.Transcation.id, models.Transcation.product_type
#                     )
#                     .order_by(desc(models.Transcation.id))
#                     .first()
#                 )
#                 result = data
#                 await websocket.send_text(f"yay Message text was lee")
#                 previous_count = current_count
#             await websocket.send_text(f"yay Message text was lee")
#     except WebSocketDisconnect:
#         ds_con_manager.disconnect(websocket=websocket)


# @ds_orders_router.get(
#     "/orders/check",
#     description="check orders in transcations.",
#     response_model=str,
# )
# def check_order_count(
#     db: Session = Depends(get_db),
# ):
#     x = (
#         db.query(func.count(models.Transcation.id))
#         .filter(models.Transcation.product_type == Product.ds)
#         .scalar()
#     )
#     return x
