import random
import datetime
from typing import List, Optional

from support.db.audios import audios
from support.models.audio import Audio
from .base import BaseRepository

from  sqlalchemy.sql.expression import func

class AudioRepository(BaseRepository):

    async def get_all(self, limit: int = 100, skip: int = 0) -> List[Audio]:
        query = audios.select().limit(limit).offset(skip)
        return await self.database.fetch_all(query=query)

    async def get_by_id(self, id: int) -> Optional[Audio]:
        query = audios.select().where(
            audios.c.message_id==id and audios.c.is_banned==False
            ).order_by(func.random()).limit(1)
        user = await self.database.fetch_one(query)
        if user is None:
            return None
        return Audio.parse_obj(user)

    async def get_random(self) -> Optional[Audio]:
        query = audios.select().where(audios.c.is_banned==False)
        res = await self.database.fetch_all(query=query)
        if len(res) == 0:
            return None
        audio = random.choice(res)
        return Audio.parse_obj(audio)

    async def create(self, u: Audio) -> Audio:
        values = {**u.dict()}
        values.pop("db_id", None)
        query = audios.insert().values(**values)
        u.db_id = await self.database.execute(query)
        return u

    async def update(self, id: int, u: Audio) -> Audio:
        values = {**u.dict()}
        values.pop("db_id", None)
        query = audios.update().where(audios.c.message_id==id).values(**values)
        await self.database.execute(query)
        return u

