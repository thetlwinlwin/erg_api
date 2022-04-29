from pydantic import BaseModel, validator
from datetime import datetime
from factory.schema.customer_schema import CustomerDetail
from factory.schema.manager_schema import ManagerBase
from factory.utils import (
    DeckSheetEnv,
    LOCAL_TIME_ZONE,
    ProductionStage,
    TransType,
    Product,
)
from fastapi import HTTPException, status


class DSOrderDetailCreate(BaseModel):
    depth: float
    length_per_sheet: float
    no_of_sheets: int
    total_length: float | None
    thickness: float
    zinc_grade: int
    pick_up_time: datetime
    production_stage: ProductionStage = ProductionStage.pending
    notes: str | None

    class Config:
        orm_mode = True
        use_enum_values = True

    @validator("depth")
    @classmethod
    def is_depth_valid(cls, value):
        if value not in DeckSheetEnv.get_depth():
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Depth is not valid.",
            )
        return value

    @validator("total_length", always=True)
    @classmethod
    def fill_total_length(cls, value, values):
        check_length = values["length_per_sheet"] * values["no_of_sheets"]
        if value is None:
            return check_length
        else:
            if value != check_length:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="something went wrong.",
                )
            return value

    @validator("thickness")
    @classmethod
    def is_thickness_valid(cls, value):
        if not DeckSheetEnv.verify_thickness(value):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Thickness is not valid.",
            )
        return value

    @validator("zinc_grade")
    @classmethod
    def is_zinc_grade_valid(cls, value):
        if value not in DeckSheetEnv.get_zinc_grade():
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Zinc_grade is not valid.",
            )
        return value

    @validator("pick_up_time")
    @classmethod
    def is_future_date(cls, value: datetime):
        if value < datetime.utcnow().astimezone(LOCAL_TIME_ZONE):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid future date.",
            )
        return value


class DSOrderCreate(BaseModel):
    customer_id: int
    ds_order_detail: DSOrderDetailCreate


class DSOrderDetailOut(BaseModel):
    id: int
    depth: float
    total_length: float
    length_per_sheet: float
    no_of_sheets: int
    thickness: float
    zinc_grade: int
    pick_up_time: datetime
    production_stage: ProductionStage
    notes: str | None

    class Config:
        orm_mode = True
        use_enum_values = True


class DSOrderOut(BaseModel):
    id: int
    ds_manager: ManagerBase
    ds_customer: CustomerDetail
    ds_order_detail: DSOrderDetailOut

    class Config:
        orm_mode = True
