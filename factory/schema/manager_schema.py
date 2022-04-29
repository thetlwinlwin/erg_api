from datetime import datetime
from pydantic import BaseModel
from factory.utils import ManagerType


class ManagerBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class ManagerCreate(ManagerBase):
    password: str
    type: ManagerType

    class Config:
        use_enum_values = True


class ManagerInfo(ManagerBase):
    created_at: datetime
    type: ManagerType

    class Config:
        use_enum_values = True
