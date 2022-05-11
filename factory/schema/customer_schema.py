from factory import utils
from fastapi import HTTPException, status
from pydantic import BaseModel, validator


class CustomerBase(BaseModel):
    name: str
    phone: str

    @validator("phone")
    @classmethod
    def is_phone_valid(cls, value: str) -> str:
        if not value.isdigit():
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid Phone Number.",
            )
        if len(value) > 11:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid Phone Number.",
            )
        return value

    class Config:
        orm_mode = True


class CustomerDetail(CustomerBase):
    address: str | None
    gender: utils.Gender

    class Config:
        use_enum_values = True
        orm_mode = True


class CustomerUpdate(BaseModel):
    name: str | None
    phone: str | None
    address: str | None
    gender: utils.Gender | None

    class Config:
        use_enum_values = True


class CustomerOut(CustomerDetail):
    """This class is for orders. if customer apply orders, it only needs its id."""

    id: int

    class Config:
        orm_mode = True
