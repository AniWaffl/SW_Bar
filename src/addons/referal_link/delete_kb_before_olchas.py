from loguru import logger
from aiogram import types

from config import dp, bot

logger.debug("delete kb loaded")

@dp.message_handler(
    text='🚩 Начать игру!',
    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP], 
)
async def delete_kb_handler(message: types.Message):
    reply_text = "Удаляю клавиатуру . . ."
    await message.reply(reply_text, reply_markup=types.ReplyKeyboardRemove())