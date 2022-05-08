from typing import Optional

from pydantic import BaseModel


# Shared properties
class ResourceBase(BaseModel):
    name: str
    icon: Optional[str] = None
    count: Optional[int] = 0
    need_to_store: Optional[int] = 0


# Properties to receive via API on creation
class ResourceCreate(ResourceBase):
    name: str


# Properties to receive via API on update
class ResourceUpdate(ResourceBase):
    pass


class ResourceInDBBase(ResourceBase):
    id: Optional[int] = None


# Additional properties to return via API
class Resource(ResourceInDBBase):
    pass


# Additional properties stored in DB
class ResourceInDB(ResourceInDBBase):
    pass
