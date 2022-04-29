from datetime import datetime
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Depends,
    Request,
    Response,
    BackgroundTasks,
)

from sqlalchemy.orm import Session
from factory import models, oauth2
from factory.database import get_db
from factory.routers.c_channel.holes_utils import saving_holes_image
from factory.schema import token_schema, c_channel_schema, orders_update_schema
from sqlalchemy import exc, func
from factory.utils import BasePath, Product, ProductionStage

cchannel_orders_router = APIRouter(
    prefix="/cchannel",
    tags=["C Channel"],
)


@cchannel_orders_router.get(
    "/orders/all",
    description="The data is sorted by pick_up_time by default.",
    response_model=list[c_channel_schema.CChannelOrderOut],
)
def get_all_orders(
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    results = (
        db.query(models.CChannelOrder)
        .join(models.CChannelOrderDetails)
        .order_by(models.CChannelOrderDetails.pick_up_time.asc())
        .filter(models.CChannelOrderDetails.production_stage != ProductionStage.done)
    ).all()

    return results


@cchannel_orders_router.put("/orders/details/update/{id}")
def update_an_order(
    id: int,
    order: orders_update_schema.OrderDetailUpdate,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_listener),
):
    order_query = db.query(models.CChannelOrderDetails).filter(
        models.CChannelOrderDetails.id == id
    )
    if order_query.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connect to the Admin.",
        )
    order_query.update(order.dict(), synchronize_session=False)
    db.commit()
    return


@cchannel_orders_router.get(
    "/orders/search/customer_info",
    description="Search orders by customer info.",
    response_model=list[c_channel_schema.CChannelOrderOut],
)
def search_order(
    request: Request,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    try:
        query_params = request.query_params._dict
        results_query = (
            db.query(models.CChannelOrder)
            .join(models.CChannelOrderDetails)
            .order_by(models.CChannelOrderDetails.pick_up_time.asc())
            .filter(
                models.CChannelOrderDetails.production_stage != ProductionStage.done
            )
            .join(models.Customer)
            .filter_by(**query_params)
        )

        return results_query.all()
    except exc.InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invaild Search Query. Check the parameters again.",
        )


@cchannel_orders_router.delete(
    "/orders/delete/{id}",
    description="delete the existing order",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_an_order(
    id: int,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    order_to_delete: models.CChannelOrder = (
        db.query(models.CChannelOrder).filter(models.CChannelOrder.id == id).first()
    )
    if order_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The order does not exist.",
        )
    # use this method to catch order object to be deleted in event listener (before_delete).
    if (
        order_to_delete.cchannel_order_detail.production_stage
        == ProductionStage.pending
    ):
        db.delete(order_to_delete)
        db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The order is either done or producing and it cannot be stopped.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@cchannel_orders_router.post("/create")
async def create_order(
    # Warning: The File parameter on the POST method must go first, before other Form parameters. Otherwise the end-point returns HTTP code 422.
    background_task: BackgroundTasks,
    file: UploadFile | None = File(None),
    customer_id: int = Form(...),
    channel_height: float = Form(...),
    channel_width: float = Form(...),
    length_per_sheet: float = Form(...),
    no_of_sheets: int = Form(...),
    thickness: float = Form(...),
    zinc_grade: int = Form(...),
    pick_up_time: datetime = Form(...),
    notes: str | None = Form(None),
    production_stage: ProductionStage | None = Form(...),
    db: Session = Depends(get_db),
    # manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):

    try:
        order_detail_scheme = c_channel_schema.CChannelOrderDetailCreate(
            channel_height=channel_height,
            channel_width=channel_width,
            production_stage=production_stage,
            length_per_sheet=length_per_sheet,
            no_of_sheets=no_of_sheets,
            thickness=thickness,
            zinc_grade=zinc_grade,
            pick_up_time=pick_up_time,
            notes=notes,
        )
        pydantic_scheme = c_channel_schema.CChannelOrderCreate(
            customer_id=customer_id,
            cchannel_order_detail=order_detail_scheme,
        )
        # TODO: replace manager_id.
        new_order = models.CChannelOrder(
            manager_id=1, customer_id=pydantic_scheme.customer_id
        )
        new_order.cchannel_order_detail = models.CChannelOrderDetails(
            **pydantic_scheme.cchannel_order_detail.dict()
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        new_order_id = new_order.id
        if file:
            file_type = file.content_type.split("/")
            if "image" not in file_type:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Unsupported file type.",
                )
            holes_path = BasePath.joinpath(f"{new_order_id}.{file_type[1]}")
            background_task.add_task(
                saving_holes_image,
                file,
                holes_path,
            )
            db.query(models.CChannelOrderDetails).filter(
                models.CChannelOrderDetails.cchannel_order_id == new_order_id
            ).update(
                {
                    models.CChannelOrderDetails.holes: str(holes_path),
                },
                synchronize_session=False,
            )
            db.commit()

    except HTTPException as e:
        raise e
