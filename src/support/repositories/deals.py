from typing import List, Optional
from support.db.deals_on_market import deals_on_market as model
from support.models.deals import Deal as ModelType
from support.models.deals import DealCreate as CreateSchemaType
from support.models.deals import DealUpdate as UpdateSchemaType
from .base import BaseRepository

class DealRepository(BaseRepository):

    async def get(self, *, id: int) -> Optional[ModelType]:
        q = model.select().where(model.c.id == id)
        res = await self.database.fetch_one(q)
        return ModelType.parse_obj(res) or None


    async def get_all(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        q = model.select().limit(limit).offset(skip)
        res = await self.database.fetch_all(query=q)
        return [ModelType.parse_obj(**i) for i in res] or None 


    async def create(self, *, m: CreateSchemaType) -> ModelType:
        values = {**m.dict()}
        values.pop("id", None)
        q = model.insert().values(**values)
        m: ModelType = ModelType(**values)
        m.id = await self.database.execute(q)
        return m


    async def update(self, *, id: int, m: UpdateSchemaType) -> ModelType:
        values = {**m.dict()}
        values.pop("id", None)
        m: ModelType = ModelType(**values)
        q = model.update().where(model.c.id==id).values(**values)
        m.id = await self.database.execute(q)
        return m


    async def remove(self, *, id: int) -> ModelType:
        q = model.delete().where(model.c.id==id)
        return await self.database.execute(q)


resource = DealRepository()