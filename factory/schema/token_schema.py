from pydantic import BaseModel
from factory.utils import ManagerType
from datetime import datetime


class PayloadData(BaseModel):
    manager_id: int | None
    manager_type: ManagerType

    class Config:
        use_enum_values = True


class PayloadDataCreate(PayloadData):
    exp: None | datetime


class Token(BaseModel):
    token_type: str
    access_token: str


# this is for refreshing token.
class RefreshToken(BaseModel):
    accepted_token: str


class TokenCreate(Token):
    refresh_token: str
