import datetime
from typing import List, Optional

from support.db.recipes import recipes
from support.models.recipe import Recipe
from .base import BaseRepository

from sqlalchemy import desc


class RecipeRepository(BaseRepository):

    async def get_all(self, limit: int = 100, skip: int = 0) -> List[Recipe]:
        query = recipes.select().limit(limit).offset(skip)
        return await self.database.fetch_all(query=query)

    async def get_by_id(self, id: int) -> Optional[Recipe]:
        query = recipes.select().where(recipes.c.db_id==id)
        user = await self.database.fetch_one(query)
        if user is None:
            return None
        return Recipe.parse_obj(user)

    async def get_by_day(self, ) -> Optional[List[Recipe]]:
        # query = recipes.select().order_by(desc(recipes.c.db_id)).limit(1)
        # print(query)
        query = """SELECT * FROM recipes WHERE date('now','-1 day') < recipes.date"""
        recipe = await self.database.fetch_all(query)
        print(recipe)
        if recipe is None:
            return None
        recipe_list: List[Recipe] = []
        for r in recipe:
            recipe_list.append(Recipe.parse_obj(r))
        return recipe_list

    async def create(self, u: Recipe) -> Recipe:
        u.date = datetime.datetime.utcnow()

        values = {**u.dict()}
        values.pop("db_id", None)
        query = recipes.insert().values(**values)
        u.db_id = await self.database.execute(query)
        return u

    # async def delete(self, id: int) -> bool:
    #     query = recipes.delete().where(recipes.c.id==id)
    #     res = await self.database.execute(query)
    #     return res

recipe = RecipeRepository()