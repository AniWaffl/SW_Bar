from typing import List, Optional, Union

from aiogram.types import chat
from config import dp, bot
from aiogram import Bot, Dispatcher, types
# from loader import bot, dp, storage
# from filters import IsAdmin
import random
# from utils.db_api.db import Smoothie_db
# from middlewares.smoothie_algo import _main as smoothie
from datetime import datetime
import config as cfg

from loguru import logger

from support.models.recipe import Recipe
from support.models.chat import Chat
from support.models.user import User 

# Repos
from support.repositories.users import UserRepository
from addons.smoothie.smoothie_api import (all_recipe, generate_list_to_remove)

logger.debug("smoothie loaded")

import timeit
class Smootie():
    _smoothies: List[Recipe] = []
    _possible_recipe: List[int] = all_recipe()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Smootie, cls).__new__(cls)
        return cls.instance

    def add_recipe(self, from_user, recipe, pos_find, bonus) -> Recipe:
        new_recipe = Recipe(
            from_user = from_user,
            recipe = recipe,
            pos_find = pos_find,
            bonus = bonus,
        )
        self._smoothies.append(new_recipe)

        self._possible_recipe = generate_list_to_remove(
            self._possible_recipe,
            new_recipe.recipe,
            new_recipe.pos_find, 
            )
        return new_recipe

    def send_best(self, ) -> Union[Recipe, bool]:
        for i in self._smoothies:
            i:Recipe
            if i.pos_find == 5:
                return i
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
        return text
        pass

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
    
    def discard(self, ) -> bool:
        self._smoothies = []
        self._possible_recipe = all_recipe()

    async def log_smoothie(self, r: Recipe, admin_chat:int = cfg.SMOOTHIE_LOG_CHAT_ID) -> bool:
        await bot.send_message(admin_chat,
                f"<a href ='tg://user?id={r.from_user}'>{r.from_user}</a>"
                f"Приготовил смузи\n"
                f"🍹 Рецепт: {r.recipe}\n"
                f"💠 Отгадано: {r.pos_find}",
                parse_mode="html")


# Основной триггер
@dp.message_handler(text='🍹Смузи')
@dp.message_handler(commands=["smoothie"])
async def get_smoothie(message: types.Message, Chat:Chat, User:User, sm:Smootie = Smootie()):
    a = sm.send_best()
    if a:
        user: User = await UserRepository().get_by_id(a.from_user)
        text_best_smoothie = (
            f"<b>😍 Самый шикарный смузи на сегодня\n</b>"
            f"<b>Приготовил:</b> <a href ='tg://user?id={user.id}'>{str(user.name)}</a>\n\n"
            f"<b>Рецепт:</b> <code>{sm.to_smile(a.recipe)}</code>\n\n"
            f"<b>Бонус:</b> {a.bonus}\n")
        await message.answer(text_best_smoothie, parse_mode="html")
    else:
        await message.answer(
            f"Попытай удачу в нахождении лучшего смузи, возможные варианты:{sm.get_variant(5)}"
            )


@dp.message_handler(regexp='Ты приготовил 🍹Смузи')
async def get_smoothie_from_SW(message: types.Message, User:User, Chat:Chat, sm:Smootie = Smootie()):
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Проверка что еще нет лучшего смузи
    best = sm.send_best()
    if best:
        await message.answer("Опоздал, лучший смузи уже найден\n /smoothie")
        return

    # Проверка на свежий форвард
    if not message.forward_from\
        or not message.forward_from.id  == cfg.SW_BOT_ID\
        or not now.date() == message.forward_date.date():
        logger.info(f"Пользователь c id {User.name} {User.id} Отправил невалидный смузи")
        await message.answer("Я принимаю только сегодняшние форварды смузи от @StartupWarsBot")
        return

    # # Проверка что пользователь в белом списке
    # if not db.user_in_whitelist(message.from_user.id):
    #     logger.info(f"Пользователя c id {message.from_user.id} нет в вайтлисте")
    #     await message.answer("Тебя нет в вайтлисте, если ты сотрудник ⚡️Stark Ind тебя обязательно добавят")
    #     btn = types.InlineKeyboardButton('Добавить в белый список', callback_data=f'add_smoothie_user_{message.from_user.id}')
    #     kb = types.InlineKeyboardMarkup().add(btn)
    #     await bot.send_message(config.admin_chat,
    #         f"<a href ='tg://user?id={message.from_user.id}'>{username.full_name}</a> "
    #         f"приготовил смузи но его нет в вайтлисте\n\n"
    #         f"<code>{message.text}</code>",
    #         parse_mode="html",
    #         reply_markup=kb)
    #     return


    # Обрабатывает форвард и пишет в БД
    rp = sm.add_recipe(
        User.id,
        sm.to_nums(message.text), 
        sm.parse_pos_find(message.text), 
        sm.parse_bonus(message.text)
        )
    raise
    await bot.send_message(cfg.SMOOTHIE_LOG_CHAT_ID,
            f"<a href ='tg://user?id={rp.from_user}'>{User.name}</a> "
            f"Приготовил смузи\n"
            f"🍹 Рецепт: {sm.to_smile(rp.recipe)}\n"
            f"💠 Отгадано: {rp.pos_find}\n"
            f"<b>Бонус:</b> {rp.bonus}\n",
            parse_mode="html")

    if rp.pos_find == 5:
        await message.answer("Ты приготовил смузи дня 🥂 Поздравляю!")

        # Отправка на канал
        text_best_smoothie = (
            f"<b>Рецепт:</b> <code>{sm.to_smile(rp.recipe)}</code>\n\n"
            f"<b>Приготовил:</b> <a href ='tg://user?id={User.id}'>{User.name}</a>\n\n"
            f"<b>Бонус:</b> {rp.bonus}\n")

        await bot.send_message(cfg.SMOOTHIE_CHANNEL_ID,
                text_best_smoothie,
                parse_mode="html")
        return

    await message.answer(
        f"Спасибо, я принял твой рецепт, несколько вероятных смузи:{sm.get_variant(5)}"
        )
    
    


# # Колбек на добавление пользователей в вайтлист
# @dp.callback_query_handler(IsAdmin(),lambda c: c.data and c.data.startswith('add_smoothie_user_'))
# async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
#     user_id = callback_query.data[18:]
#     msg_id = callback_query.message.message_id
#     chat_id = callback_query.message.chat.id

#     who = await bot.get_chat(int(user_id))

#     db.add_id_to_smoothie_users(user_id)
#     await bot.answer_callback_query(callback_query.id, text='Пользователь добавлен')
#     await bot.delete_message(chat_id, msg_id)

#     logger.info(callback_query.from_user)
#     await bot.send_message(chat_id,
#         f"<a href ='tg://user?id={callback_query.from_user.id}'>{callback_query.from_user.first_name}</a> "
#         f"добавил <a href ='tg://user?id={who.id}'>{who.full_name}</a>",
#         parse_mode="html")


