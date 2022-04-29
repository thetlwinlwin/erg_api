from pydantic import BaseModel

from factory import utils


class OrderDetailUpdate(BaseModel):
    production_stage: utils.ProductionStage

    class Config:
        use_enum_values = True
