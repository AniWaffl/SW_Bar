import re
from aiogram import types
from main import dp
from support.models.chat import Chat
from loguru import logger
from addons.utils.keyboards import bool_icon

logger.debug("settings loaded")

module_naming = {
    "Triggers": "Триггеры",
    "AdminOnly": "Admin Only",
    "Welcome": "Приветствие",
    "Captcha": "Капча",
    "EasyAdmin": "Easy Admin",
    "Reports": "Репорты",
    "Games": "Игры",
    "Cats": "Животные"
}


@dp.message_handler(
    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
    is_chat_admin=True,
    commands="settings",
    commands_prefix="!"
)
async def get_settings_keyboard(message: types.Message, Chat: Chat):
    await message.answer("Настройки чата", reply_markup=settings_keyboard(Chat))


@dp.callback_query_handler(
    chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
    is_chat_admin=True,
    regexp=r"^settings-(?P<settings>.*)"
)
async def switch_settings(call: types.CallbackQuery, regexp: re.Match, Chat: Chat):
    settings_type = regexp.group("settings")
    if settings_type in Chat.modules:
        Chat.modules[settings_type] = not Chat.modules[settings_type]
    else:
        await call.answer("Эта настройка была удалена", show_alert=True)
        return
    await Chat.save()
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=settings_keyboard(Chat))


def settings_keyboard(chat: Chat) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for module, value in chat.modules.items():
        keyboard.insert(types.InlineKeyboardButton(f"{bool_icon(value)} {module_naming[module]}", callback_data=f"settings-{module}"))
    return keyboard
