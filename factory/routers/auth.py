from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from factory.database import get_db
from factory import models
from factory.utils import verify, hashing
from factory import oauth2
from factory.schema import manager_schema, token_schema
from sqlalchemy import exc
from psycopg2.errors import UniqueViolation

auth_router = APIRouter(prefix="/manager", tags=["authentication", "Manager"])


@auth_router.post("/login", response_model=token_schema.TokenCreate)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    manager = (
        db.query(models.Manager)
        .filter(models.Manager.name == form_data.username)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password"
        )
    if not verify(form_data.password, manager.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password"
        )
    data = token_schema.PayloadDataCreate(
        manager_id=manager.id,
        manager_type=manager.type,
    )
    access_token = oauth2.create_access_token(data=data)
    refresh_token = oauth2.create_refresh_token(data=data)
    return token_schema.TokenCreate(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@auth_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=manager_schema.ManagerInfo,
)
def create(info: manager_schema.ManagerCreate, db: Session = Depends(get_db)):
    # if ManagerType.is_admin(info.type):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Contact support for more info.",
    #     )
    info.password = hashing(password=info.password)
    new_manager = models.Manager(**info.dict())
    db.add(new_manager)
    try:
        db.commit()
    except exc.IntegrityError as e:
        assert isinstance(e.orig, UniqueViolation)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid name"
        )
    db.refresh(new_manager)
    return new_manager


@auth_router.post("/refresh", response_model=token_schema.TokenCreate)
def refresh(accepted_token: token_schema.RefreshToken):
    print("accepted_token")
    print(accepted_token)
    return oauth2.renew_token(accepted_token.accepted_token)
