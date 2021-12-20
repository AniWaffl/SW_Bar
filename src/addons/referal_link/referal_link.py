from loguru import logger
from aiogram import types

from config import dp, bot

logger.debug("reflink loaded")

BASE62 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


@dp.message_handler(
    commands=["reflink"],
    chat_type=[types.ChatType.PRIVATE],
)
async def reflink_handler(message: types.Message):
    argument = message.get_args()

    if not argument:
        await message.answer(
            f"Я помогаю узнавать id пользователя по его реферальной ссылке и наоборот\n"
            f"Пиши /reflink <b>user_id</b> или /reflink <b>MyGаН</b>\n"
            f"<code>t.me/StartupWarsBot?start=</code><b>MyGаН</b>",
            disable_web_page_preview=True,
            parse_mode="HTML"
        )
        return

    try:
        argument = int(argument)
        user_ref = encode(argument)
        await message.answer(
            f"Реферальная ссылка человека с id - <b>{argument}</b>:\n"
            f"t.me/StartupWarsBot?start={user_ref}",
            disable_web_page_preview=True,
            parse_mode="HTML"
        )

    except:
        a = decode(str(argument))
        await message.answer(
            f"id человека с рефкой - {argument}:   "
            f"<code>{a}</code>\nВозможно скоро я смогу давать больше информации",
            disable_web_page_preview=True,
            parse_mode="HTML"
        )


def encode(num, alphabet=BASE62):
    if num == 0:
        return alphabet[0]
    arr = []
    arr_append = arr.append 
    _divmod = divmod  
    base = len(alphabet)
    while num:
        num, rem = _divmod(num, base)
        arr_append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def decode(string, alphabet=BASE62):

    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num