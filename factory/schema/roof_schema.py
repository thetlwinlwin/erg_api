from pydantic import BaseModel, validator
from datetime import datetime
from factory.schema.customer_schema import CustomerDetail
from factory.schema.manager_schema import ManagerBase
from factory import utils
from fastapi import HTTPException, status


class RoofOrderDetailCreate(BaseModel):
    color: str
    manufacturer: utils.ColorPlainManufacturer
    length_per_sheet: float
    no_of_sheets: int
    total_length: float | None
    thickness: float
    pick_up_time: datetime
    production_stage: utils.ProductionStage = utils.ProductionStage.pending
    notes: str | None

    class Config:
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

    @validator("thickness")
    @classmethod
    def is_thickness_valid(cls, value):
        if not utils.RoofEnv.verify_thickness(value):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Thickness is not valid.",
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


class RoofOrderCreate(BaseModel):
    customer_id: int
    roof_order_detail: RoofOrderDetailCreate


class RoofOrderDetailOut(BaseModel):
    id: int
    color: str
    manufacturer: utils.ColorPlainManufacturer
    length_per_sheet: float
    no_of_sheets: int
    total_length: float | None
    thickness: float
    pick_up_time: datetime
    production_stage: utils.ProductionStage = utils.ProductionStage.pending
    notes: str | None

    class Config:
        orm_mode = True
        use_enum_values = True


class RoofOrderOut(BaseModel):
    id: int
    roof_manager: ManagerBase
    roof_customer: CustomerDetail
    roof_order_detail: RoofOrderDetailOut

    class Config:
        orm_mode = True
