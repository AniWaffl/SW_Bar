import datetime
from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    db_id: Optional[int]
    id: int
    name: str
    username: Optional[str] = None
    is_private_msg: bool
    is_admin: bool = False
    is_banned: bool = False
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

