import datetime
from typing import Optional
from pydantic import BaseModel


class Audio(BaseModel):
    db_id: Optional[int]
    message_id: int
    title: str
    performer: str
    file_id: str
    duration: int
    is_banned: bool = False
    created_at: datetime.datetime = datetime.datetime.utcnow()
