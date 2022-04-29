from pydantic import BaseModel
from factory import utils


class CheckOrderByIdResponse(BaseModel):
    product_type: utils.Product
    transcation_type: utils.TransType

    class Config:
        orm_mode = True
        use_enum_values = True


class OrderCount(BaseModel):
    product_type: utils.Product
    count: int = 0

    def __sub__(self, p2):
        if isinstance(p2, OrderCount):
            if p2.product_type == self.product_type:
                x = self.count - p2.count
                return OrderCount(
                    product_type=self.product_type,
                    count=x,
                )
            else:
                raise Exception("They must have same ProductType")
        else:
            raise Exception("They must has same class")

    def __eq__(self, other):
        if not isinstance(other, OrderCount):
            raise Exception("They must has same class")
        return self.product_type == other.product_type

    class Config:
        use_enum_values = True
        orm_mode = True


# class StreamOrder(BaseModel):
#     orders: list[OrderCount]

#     class Config:
#         use_enum_values = True
