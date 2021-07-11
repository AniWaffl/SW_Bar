import datetime
from typing import Optional
from pydantic import BaseModel


class Chat(BaseModel):
    db_id: Optional[int]
    id: int
    username: Optional[str] = None
    title: str
    invite_link: Optional[str]
    is_banned: bool = False
    
    is_parse_smoothie: bool = False

    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

