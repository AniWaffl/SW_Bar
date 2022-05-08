import datetime
from typing import List, Optional
from support.db.users import users
from support.models.user import User
from .base import BaseRepository

class UserRepository(BaseRepository):

    async def get_all(self, limit: int = 100, skip: int = 0) -> List[User]:
        query = users.select().limit(limit).offset(skip)
        return await self.database.fetch_all(query=query)

    async def get_by_id(self, id: int) -> Optional[User]:
        query = users.select().where(users.c.id==id)
        user = await self.database.fetch_one(query)
        if user is None:
            return None
        return User.parse_obj(user)

    async def create(self, u: User) -> User:
        u.created_at = datetime.datetime.utcnow()
        u.updated_at = datetime.datetime.utcnow()

        values = {**u.dict()}
        values.pop("db_id", None)
        query = users.insert().values(**values)
        u.id = await self.database.execute(query)
        return u

    async def update(self, id: int, u: User) -> User:
        u.updated_at = datetime.datetime.utcnow()
        values = {**u.dict()}
        values.pop("db_id", None)
        query = users.update().where(users.c.id==id).values(**values)
        await self.database.execute(query)
        return u

user = UserRepository()