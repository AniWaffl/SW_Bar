import datetime
from pydantic import BaseModel


class Reaction(BaseModel):
    channel_id: int
    message_id: int
    user_id: int
    created_at: datetime.datetime = datetime.datetime.utcnow()
