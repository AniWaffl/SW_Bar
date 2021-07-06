from aiogram import types


def get_cancel_button() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.insert(types.KeyboardButton("Отменить"))
    return keyboard


def bool_icon(info: bool) -> str:
    if info:
        return "🟢"
    else:
        return "🔴"
