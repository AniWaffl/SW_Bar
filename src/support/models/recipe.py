import datetime
from typing import Optional
from pydantic import BaseModel

class Recipe(BaseModel):
    db_id: Optional[int]
    from_user: int
    recipe: str
    pos_find: int
    bonus: Optional[str] = None
    date: datetime.datetime = datetime.datetime.utcnow()