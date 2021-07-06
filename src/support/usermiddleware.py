from typing import Union

import config as cfg
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from loguru import logger

# Database Repos
from support.repositories.users import UserRepository
from support.repositories.chats import ChatRepository

# Dataclasses
from support.models.user import User
from support.models.chat import Chat


class UserMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super(UserMiddleware, self).__init__()

    async def pre_process(self, update: Union[types.ChatMemberUpdated, types.Message, types.CallbackQuery], data: dict):
        user, chat = await self.validate(update)

        data["User"] = user
        data["Chat"] = chat
        # data["mongo"] = mongo
        # data["redis"] = redis
        # data["scheduler"] = scheduler

    async def post_process(self, update: Union[types.ChatMemberUpdated, types.Message, types.CallbackQuery], *args):
        pass


    async def validate(self, update: Union[types.Message, types.CallbackQuery, types.ChatMemberUpdated]):# -> Tuple[UserType, Union[ChatType, None]]:

        if isinstance(update, types.CallbackQuery):
            User = update.from_user
            Chat = update.message.chat

        elif isinstance(update, types.Message):
            User = update.from_user
            Chat = update.chat

        elif isinstance(update, types.ChatMemberUpdated):
            User = update.new_chat_member.user
            Chat = update.chat

        else:
            logger.warning(f"Update is not supported {types(update)}")
            raise CancelHandler()

        if User.id == 777000:
            raise CancelHandler()

        user = await self.get_user(User, update)

        if user.is_banned:
            raise CancelHandler()

        chat = None

        if Chat.type != "private":
            chat = await self.get_chat(Chat)

            if chat.is_banned:
                raise CancelHandler()

        return user, chat

    async def get_user(
        self, 
        user: types.User, 
        update: Union[types.Message, types.CallbackQuery], 
        users: UserRepository = UserRepository(),
        ) -> User:

        user_db = await users.get_by_id(user.id)
        
        to_pm = False
        chat_id = None

        if isinstance(update, types.CallbackQuery):
            if update.message.chat.type == "private":
                to_pm = True
            else:
                chat_id = update.message.chat.id
        else:
            if update.chat.type == "private":
                to_pm = True
            else:
                chat_id = update.chat.id

        if user_db:
            user_db.name = user.full_name
            user_db.username = user.username or None
            user_db.is_private_msg = to_pm if to_pm else user_db.is_private_msg
            user_db.is_admin = True if user_db.id in cfg.admins else user_db.is_admin

            await users.update(user_db.id, user_db)
            return user_db

        user_db = User(
            id = user.id,
            name = user.full_name,
            username = user.username or None,
            is_private_msg = to_pm if to_pm else False)

        user_db = await users.create(user_db)
        return user_db


    async def get_chat(
        self, 
        chat: types.Chat, 
        chats: ChatRepository = ChatRepository(),
        ):
        chat_db = await chats.get_by_id(chat.id)

        if chat_db:
            chat_db.title = chat.title
            chat_db.username = chat.username or None
            chat_db.invite_link = chat.invite_link or None
            if not chat_db.invite_link:
                try:
                    chat_db.invite_link = await chat.export_invite_link()
                except Exception:
                    pass

            await chats.update(chat_db.id, chat_db)
            return chat_db

        chat_db = Chat(
            id = chat.id,
            username = chat.username or None,
            is_banned = False,
            title = chat.title,
            invite_link = chat.invite_link or None,
            )

        if not chat_db.invite_link:
            try:
                chat_db.invite_link = await chat.export_invite_link()
            except Exception:
                pass

        chat_db = await chats.create(chat_db)

        return chat_db
