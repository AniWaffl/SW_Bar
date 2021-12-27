import asyncio

from loguru import logger
from aiogram import types, Bot
from aiogram.types.message import ContentType


import config as cfg
from config import dp, bot

# Models
from support.models.chat import Chat
from support.models.user import User


# Repos
from support.repositories.users import UserRepository

logger.debug("resend_audio loaded")


@dp.message_handler(
    content_types=ContentType.AUDIO,
    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
    )
async def send_audio_to_channel(message: types.Message, Chat: Chat, User: User):
    caption = [
        f"🎙 <a href ='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
    ]

    message = await bot.send_audio(
        cfg.RADIO_CHANNEL_ID, 
        message.audio.file_id, 
        "\n".join(caption), 
        disable_notification=True,
        )