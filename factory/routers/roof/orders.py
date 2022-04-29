from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    Request,
    Response,
)

from sqlalchemy.orm import Session
from factory import models, oauth2
from factory.database import get_db
from factory.schema import token_schema, roof_schema, orders_update_schema
from sqlalchemy import exc, func
from factory.utils import ProductionStage

roof_orders_router = APIRouter(
    prefix="/roof",
    tags=["Roof"],
)


@roof_orders_router.get(
    "/orders/all",
    description="The data is sorted by pick_up_time by default.",
    response_model=list[roof_schema.RoofOrderOut],
)
def get_all_orders(
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    results = (
        db.query(models.RoofOrder)
        .join(
            models.RoofOrderDetails,
        )
        .order_by(models.RoofOrderDetails.pick_up_time.asc())
        .filter(models.RoofOrderDetails.production_stage != ProductionStage.done)
    ).all()
    return results


@roof_orders_router.get(
    "/orders/search/customer_info",
    description="earch orders by customer info. Output will be sorted with most recent pick_up_time",
    response_model=list[roof_schema.RoofOrderOut],
)
def search_order(
    request: Request,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    try:
        query_params = request.query_params._dict
        results_query = (
            db.query(models.RoofOrder)
            .join(models.RoofOrderDetails)
            .order_by(models.RoofOrderDetails.pick_up_time.desc())
            .filter(models.RoofOrderDetails.production_stage != ProductionStage.done)
            .join(models.Customer)
            .filter_by(**query_params)
        )

        return results_query.all()
    except exc.InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invaild Search Query. Check the parameters again.",
        )


@roof_orders_router.post("/create")
def create_an_order(
    order: roof_schema.RoofOrderCreate,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    new_order = models.RoofOrder(
        manager_id=manager_info.manager_id, customer_id=order.customer_id
    )
    new_order.roof_order_detail = models.RoofOrderDetails(
        **order.roof_order_detail.dict()
    )

    db.add(new_order)
    db.commit()


@roof_orders_router.put("/orders/details/update/{id}")
def update_an_order(
    id: int,
    order: orders_update_schema.OrderDetailUpdate,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_listener),
):
    order_query = db.query(models.RoofOrderDetails).filter(
        models.RoofOrderDetails.id == id
    )
    if order_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connect to the Admin.",
        )
    order_query.update(order.dict(), synchronize_session=False)
    db.commit()
    return


@roof_orders_router.delete(
    "/orders/delete/{id}",
    description="delete the existing order",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_an_order(
    id: int,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    order_to_delete: models.RoofOrder = (
        db.query(models.RoofOrder).filter(models.RoofOrder.id == id).first()
    )
    if order_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order does not exist.",
        )
    # use this method to catch order object to be deleted in event listener (before_delete).
    if order_to_delete.roof_order_detail.production_stage == ProductionStage.pending:
        db.delete(order_to_delete)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The order is either done or producing and it cannot be stopped.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
