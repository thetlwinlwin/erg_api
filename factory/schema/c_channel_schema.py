from datetime import datetime

from factory import utils
from factory.schema.customer_schema import CustomerDetail
from factory.schema.manager_schema import ManagerBase
from fastapi import HTTPException, status
from pydantic import BaseModel, validator


class CChannelOrderDetailCreate(BaseModel):
    channel_height: float
    channel_width: float
    holes: str | None
    length_per_sheet: float
    no_of_sheets: int
    total_length: float | None
    thickness: float
    zinc_grade: int
    pick_up_time: datetime
    production_stage: utils.ProductionStage = utils.ProductionStage.pending
    notes: str | None

    class Confg:
        orm_mode = True
        use_enum_values = True

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

    @validator("channel_height")
    @classmethod
    def is_height_valid(cls, value):
        if utils.CChannelEnv.verify_height(value):
            print("verifying")
            return value
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Height is not valid"
            )

    @validator("channel_width")
    @classmethod
    def is_width_valid(cls, value):
        if utils.CChannelEnv.verify_width(value):
            return value
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Width is not valid"
            )

    @validator("thickness")
    @classmethod
    def is_thickness_valid(cls, value):
        if not utils.CChannelEnv.verify_thickness(value):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Thickness is not valid.",
            )
        return value

    @validator("zinc_grade")
    @classmethod
    def is_zinc_grade_valid(cls, value):
        if value not in utils.CChannelEnv.get_zinc_grade():
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Zinc_grade is not valid.",
            )
        return value

    @validator("pick_up_time")
    @classmethod
    def is_future_date(cls, value: datetime):
        if value < datetime.utcnow().astimezone(utils.LOCAL_TIME_ZONE):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid future date.",
            )
        return value


class CChannelOrderCreate(BaseModel):
    customer_id: int
    cchannel_order_detail: CChannelOrderDetailCreate


class CChannelOrderDetailOut(BaseModel):
    id: int
    channel_height: float
    channel_width: float
    holes: str | None
    total_length: float
    length_per_sheet: float
    no_of_sheets: int
    thickness: float
    zinc_grade: int
    pick_up_time: datetime
    production_stage: utils.ProductionStage = utils.ProductionStage.pending
    notes: str | None

    class Config:
        orm_mode = True
        use_enum_values = True


class CChannelOrderOut(BaseModel):
    id: int
    cchannel_manager: ManagerBase
    cchannel_customer: CustomerDetail
    cchannel_order_detail: CChannelOrderDetailOut

    class Config:
        orm_mode = True
