import datetime
from typing import List, Optional

from support.db.chats import chats
from support.models.chat import Chat
from .base import BaseRepository

class ChatRepository(BaseRepository):

    async def get_all(self, limit: int = 100, skip: int = 0) -> List[Chat]:
        query = chats.select().limit(limit).offset(skip)
        chat = await self.database.fetch_all(query=query)
        if chat is None:
            return None
        else:
            lst = []
            for i in chat:
                lst.append(Chat.parse_obj(i))
        return lst

    async def get_by_id(self, id: int) -> Optional[Chat]:
        query = chats.select().where(chats.c.id==id)
        user = await self.database.fetch_one(query)
        if user is None:
            return None
        return Chat.parse_obj(user)

    async def create(self, u: Chat) -> Chat:
        u.created_at = datetime.datetime.utcnow()
        u.updated_at = datetime.datetime.utcnow()

        values = {**u.dict()}
        values.pop("db_id", None)
        query = chats.insert().values(**values)
        u.id = await self.database.execute(query)
        return u

    async def update(self, id: int, u: Chat) -> Chat:
        u.updated_at = datetime.datetime.utcnow()
        values = {**u.dict()}
        values.pop("db_id", None)
        query = chats.update().where(chats.c.id==id).values(**values)
        await self.database.execute(query)
        return u

    async def delete(self, id: int) -> bool:
        query = chats.delete().where(chats.c.id==id)
        res = await self.database.execute(query)
        return res

