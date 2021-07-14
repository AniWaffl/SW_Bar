import time
import random
from datetime import datetime
from typing import List, Union

from aiogram import types
from aiogram.dispatcher.filters.builtin import IDFilter
from loguru import logger

import config as cfg
from config import dp, bot

# Models
from support.models.recipe import Recipe
from support.models.chat import Chat
from support.models.user import User

# Repos
from support.repositories.users import UserRepository
from support.repositories.recipes import RecipeRepository

from addons.smoothie.smoothie_api import (all_recipe, generate_list_to_remove)

logger.debug("smoothie loaded")


class Smootie():
    _smoothies: List[Recipe] = []
    _possible_recipe: List[int] = all_recipe()
    _date_smoothie = datetime.utcnow().date()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Smootie, cls).__new__(cls)
        return cls.instance


    def discard(self, ) -> bool:
        self._smoothies = []
        self._possible_recipe = all_recipe()
        self._date_smoothie = datetime.utcnow().date()


    async def add_recipe(self, from_user, recipe, pos_find, bonus) -> Recipe:
        # Сбросить старый смузи 
        if not self._date_smoothie == datetime.utcnow().date():
            self.discard()

        new_recipe = Recipe(
            from_user = from_user,
            recipe = recipe,
            pos_find = pos_find,
            bonus = bonus,
        )
        self._smoothies.append(new_recipe)
        await RecipeRepository().create(new_recipe)

        self._possible_recipe = generate_list_to_remove(
            self._possible_recipe,
            new_recipe.recipe,
            new_recipe.pos_find, 
            )
        return new_recipe


    def get_best(self, ) -> Union[Recipe, bool]:
        # Сбросить старый смузи 
        if not self._date_smoothie == datetime.utcnow().date():
            self.discard()

        for recipe in self._smoothies:
            recipe:Recipe
            if recipe.pos_find == 5:
                return recipe
        else:
            return False


    def get_variant(self, how_much:int) -> str:
        recipe_list = self._possible_recipe
        text = f"\n💠 Осталось {len(recipe_list)} возможных рецепта."

        if len(recipe_list) < how_much:
            how_much = len(recipe_list)

        while how_much > 0:
            random_recipe = self.to_smile(random.choice(recipe_list))
            if random_recipe in text:
                continue
            text += f"\n* <code>{random_recipe}</code>"
            how_much -= 1

        # add rp bonus to text
        lvl = 0
        bonus = ""
        for i in self._smoothies:
            if i.pos_find > lvl:
                lvl = i.pos_find
                bonus = i.bonus

        text += f"\n\n<b>🍀Бонус: </b> {bonus}"  if bonus not in ["", "Рецепт неизвестен"] else ""
        return text


    def parse_pos_find(self, text):
        if "❗️Увы, но твой смузи сегодня что-то не очень." in text:
            pos_find = 0
        elif "😐Неплохой смузи, но бывало и лучше." in text:
            pos_find = 2
        elif "😀Хороший смузи, респект." in text:
            pos_find = 3
        elif "😁Отличный смузи, поздравляю!" in text:
            pos_find = 4
        elif "😍Самый шикарный смузи на сегодня!" in text:
            pos_find = 5

        if pos_find is None:
            logger.error("Не смог определить уровень смузи")
            raise "Не смог определить уровень смузи"

        return pos_find


    def to_nums(self, recipe:str):
        """Превращает символьное значение смузи в цифровое"""
        
        user_frendly_recipe =""
        for i in list(recipe):
            if i == "🍋":
                user_frendly_recipe += "".join("1")
            if i == "🍇":
                user_frendly_recipe += "".join("2")
            if i == "🍏":
                user_frendly_recipe += "".join("3")
            if i == "🥕":
                user_frendly_recipe += "".join("4")
            if i == "🍅":
                user_frendly_recipe += "".join("5")
        return user_frendly_recipe


    def to_smile(self, recipe:int):
        """Превращает цифровое значение смузи в символьное"""

        user_frendly_recipe =""
        for i in list(recipe):
            if i == "1":
                user_frendly_recipe += "".join("🍋")
            if i == "2":
                user_frendly_recipe += "".join("🍇")
            if i == "3":
                user_frendly_recipe += "".join("🍏")
            if i == "4":
                user_frendly_recipe += "".join("🥕")
            if i == "5":
                user_frendly_recipe += "".join("🍅")
        return user_frendly_recipe


    def parse_bonus(self, text: str) -> str:
        if "❗️Увы, но твой смузи сегодня что-то не очень." in text:
            return "Рецепт неизвестен"

        elif "Этот смузи хуже предыдущего, так что бонус остаётся лучший." in text:
            return "Рецепт неизвестен"

        else:
            text = text.split("\n")
            return text[6]


    async def restart(self, ) -> bool:
        self.discard()
        l: List[Recipe] = await RecipeRepository().get_by_day()
        for recipe in l:
            await self.add_recipe(
                recipe.from_user,
                recipe.recipe,
                recipe.pos_find,
                recipe.bonus,
            )



# Перезагрузка смузи
@dp.message_handler(IDFilter(user_id=[*cfg.admins]), commands=["smoothie_restart"],)
async def restart_smoothie(message: types.Message, Chat:Chat, User:User, sm:Smootie = Smootie()):
    start_time = time.time()
    await sm.restart()
    await message.answer(f"Пересчитываю смузи ^_^ \nЗатрачено: {time.time() - start_time}сек")


# Основной триггер
@dp.message_handler(text='🍹Смузи')
@dp.message_handler(commands=["smoothie"])
async def send_smoothie(message: types.Message, Chat:Chat, User:User, sm:Smootie = Smootie()):
    a = sm.get_best()

    if not a:
        await message.answer(
            f"Попытай удачу в нахождении лучшего смузи, возможные варианты:{sm.get_variant(5)}"
            )
        return

    user: User = await UserRepository().get_by_id(a.from_user)
    text_best_smoothie = (
        f"<b>😍 Самый шикарный смузи на сегодня\n</b>"
        f"<b>Приготовил:</b> <a href ='tg://user?id={user.id}'>{str(user.name)}</a>\n\n"
        f"<b>Рецепт:</b> <code>{sm.to_smile(a.recipe)}</code>\n\n"
        f"<b>Бонус:</b> {a.bonus}\n")

    await message.answer(text_best_smoothie, parse_mode="html", disable_notification=True)


# Принимает рецепты
@dp.message_handler(
    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], 
    regexp='Ты приготовил 🍹Смузи',)
async def get_smoothie_from_SW(message: types.Message, User:User, Chat:Chat, sm:Smootie = Smootie()):
    
    if not Chat.is_parse_smoothie:
        return

    # Проверка на свежий форвард
    if  not message.forward_from or \
        not message.forward_from.id  == cfg.SW_BOT_ID or\
        not datetime.utcnow().date() == message.forward_date.date():
        
        logger.info(f"{datetime.utcnow().date()}{message.forward_date.date()}")
        logger.info(f"{message.forward_from.id } { type(cfg.SW_BOT_ID)}")
        logger.info(f"Пользователь c id {User.name} {User.id} Отправил невалидный смузи")
        await message.answer("Я принимаю только сегодняшние форварды смузи от @StartupWarsBot")
        return

    # Проверка что еще нет лучшего смузи
    if sm.get_best():
        await message.answer("Опоздал, лучший смузи уже найден\n /smoothie")
        return

    # Обрабатывает форвард и пишет в БД
    rp = await sm.add_recipe(
        User.id,
        sm.to_nums(message.text), 
        sm.parse_pos_find(message.text), 
        sm.parse_bonus(message.text)
        )

    # Логирование принятых смузи
    await bot.send_message(cfg.SMOOTHIE_LOG_CHAT_ID,
            f"<a href ='tg://user?id={rp.from_user}'>{User.name}</a> "
            f"Приготовил смузи\n"
            f"🍹 Рецепт: {sm.to_smile(rp.recipe)}\n"
            f"💠 Отгадано: {rp.pos_find}\n"
            f"<b>Бонус:</b> {rp.bonus}\n",
            parse_mode="html",
            disable_notification=True,)

    if rp.pos_find == 5:
        await message.answer("Ты приготовил смузи дня 🥂 Поздравляю!")

        # Отправка лучшего рецепта на канал
        text_best_smoothie = (
            f"<b>Рецепт:</b> <code>{sm.to_smile(rp.recipe)}</code>\n\n"
            f"<b>Приготовил:</b> <a href ='tg://user?id={User.id}'>{User.name}</a>\n\n"
            f"<b>Бонус:</b> {rp.bonus}\n")
        await bot.send_message(
            cfg.SMOOTHIE_CHANNEL_ID, 
            text_best_smoothie, 
            parse_mode="html", 
            disable_notification=True,)
        return

    await message.answer(
        f"Спасибо, я принял твой рецепт, несколько вероятных смузи:{sm.get_variant(5)}"
        )
    
