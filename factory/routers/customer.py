from factory import models, oauth2
from factory.database import get_db
from factory.schema import customer_schema, token_schema
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from psycopg2.errors import UniqueViolation
from sqlalchemy import exc
from sqlalchemy.orm import Session


customer_router = APIRouter(prefix="/customers", tags=["Customer"])


# @customer_router.get(
#     "/all",
#     description="all customers",
#     response_model=list[customer_schema.CustomerOut],
# )
# def get_all_customers(
#     db: Session = Depends(get_db),
#     manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
# ):
#     return db.query(models.Customer).all()


@customer_router.get(
    "/search",
    description="search with name,gender combination or with phone",
    response_model=list[customer_schema.CustomerOut],
)
def search_customer(
    # instead of writing each parameter. Request is more dynamic to use.
    request: Request,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):

    try:
        query_params = request.query_params._dict
        if not query_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invaild Search Query. Check the parameters again.",
            )
        results = db.query(models.Customer).filter_by(**query_params).all()
        print("here")
        if results:
            return results
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such customer.",
            )
    except exc.InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invaild Search Query. Check the parameters again.",
        )


@customer_router.post("/create", response_model=customer_schema.CustomerOut)
def create_customer(
    info: customer_schema.CustomerDetail,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    """in front end, user will find the existing customer first. that's why here we do not check if it is new customer."""
    print(info)
    new_customer = models.Customer(**info.dict())
    db.add(new_customer)
    try:
        db.commit()
    except exc.IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Duplicate phone number."
        )
    db.refresh(new_customer)
    return new_customer


@customer_router.put(
    "/update/{id}",
    description="update the existing customer",
    response_model=customer_schema.CustomerDetail,
)
def update_customer(
    id: int,
    info: customer_schema.CustomerUpdate,
    db: Session = Depends(get_db),
    manager_info: token_schema.PayloadData = Depends(oauth2.get_issuer),
):
    customer_query = db.query(models.Customer).filter(models.Customer.id == id)
    old_customer = customer_query.first()
    if old_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The customer does not exist.",
        )

    customer_query.update(info.dict(exclude_none=True), synchronize_session=False)
    db.commit()
    return customer_query.first()


# @customer_router.delete(
#     "/delete/{id}",
#     description="delete the existing customer",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_customer(
#     id: int,
#     db: Session = Depends(get_db),
#     manager_info: token_schema.PayloadData = Depends(oauth2.get_admin),
# ):
#     result = db.query(models.Customer).filter(models.Customer.id == id).first()
#     # delete returns number of rows match to be deleted.
#     # not result means not a single row has matched.
#     if result is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"The customer does not exist.",
#         )
#         # use this method to catch customer object to be deleted in event listener (before_delete).
#     db.delete(result)
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
