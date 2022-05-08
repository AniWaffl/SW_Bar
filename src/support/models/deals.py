from typing import Optional

from pydantic import BaseModel

from support.db.deals_on_market import DealOffer


# Shared properties
class DealBase(BaseModel):
    offer: DealOffer
    user_id: int
    resource_id: int
    count: int


# Properties to receive via API on creation
class DealCreate(DealBase):
    offer: DealOffer
    user_id: int
    resource_id: int
    count: int


# Properties to receive via API on update
class DealUpdate(DealBase):
    pass


class DealInDBBase(DealBase):
    id: Optional[int] = None


# Additional properties to return via API
class Deal(DealInDBBase):
    pass


# Additional properties stored in DB
class DealInDB(DealInDBBase):
    pass
