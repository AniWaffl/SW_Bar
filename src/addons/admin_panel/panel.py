import datetime as dt
import re
from asyncio import sleep

import config as cfg
import humanize
from addons.utils.trigger_helper import id_gen
from aiogram import md, types
from aiogram.utils.parts import paginate
from loguru import logger
from support.bots import dp
from support.dbmanager import FastMongo
from support.ponytypes import ChatType, LibType, UserType

logger.debug("admin panel loaded")


@dp.message_handler(
    global_admin=True,
    commands="chats_info"
)
async def chats_info(message: types.Message, mongo: FastMongo):
    args = message.get_args()
    try:
        page = int(args)
    except Exception:
        page = 0
    db_chats = mongo.get_coll(cfg.chat_collection)
    date_search = message.date - dt.timedelta(days=2)
    pipline = {"last_online": {"$gt": date_search}}
    cursor = db_chats.find(pipline)
    alldocs: int = await db_chats.count_documents(pipline)
    data = await cursor.to_list(length=None)
    show = paginate(data, page=page, limit=15)
    out = f"Активные чаты за последние 2 дня {(page + 1) * 15}/{alldocs}, страница {page}:\n\n"
    for chat in show:
        chat = ChatType(chat)
        out += chat_formatter(chat)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(f"⬅️ {page-1}", callback_data=f"admin-chat-info-{page-1}"))
    keyboard.insert(types.InlineKeyboardButton(f">{page}<", callback_data="None"))
    keyboard.insert(types.InlineKeyboardButton(f"{page+1} ➡️", callback_data=f"admin-chat-info-{page+1}"))
    await message.answer(out, reply_markup=keyboard, disable_web_page_preview=True)


@dp.callback_query_handler(
    global_admin=True,
    regexp=r"admin-chat-info-(?P<page>-?\d+)"
)
async def chat_info_callback(call: types.CallbackQuery, regexp: re.Match, mongo: FastMongo):
    page = int(regexp.group("page"))
    db_chats = mongo.get_coll(cfg.chat_collection)
    date_search = dt.datetime.now() - dt.timedelta(days=2)
    pipline = {"last_online": {"$gt": date_search}}
    cursor = db_chats.find(pipline)
    alldocs: int = await db_chats.count_documents(pipline)
    data = await cursor.to_list(length=None)
    show = paginate(data, page=page, limit=15)
    out = f"Активные чаты за последние 2 дня {(page + 1) * 15}/{alldocs}, страница {page}:\n\n"
    for chat in show:
        chat = ChatType(chat)
        out += chat_formatter(chat)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(f"⬅️ {page-1}", callback_data=f"admin-chat-info-{page-1}"))
    keyboard.insert(types.InlineKeyboardButton(f">{page}<", callback_data="None"))
    keyboard.insert(types.InlineKeyboardButton(f"{page+1} ➡️", callback_data=f"admin-chat-info-{page+1}"))
    await call.message.edit_text(out, reply_markup=keyboard, disable_web_page_preview=True)
    await call.answer()


@dp.message_handler(
    global_admin=True,
    commands="chat_info"
)
async def chat_info(message: types.Message, mongo: FastMongo):
    args = message.get_args()
    try:
        chat_id = int(args)
    except Exception:
        await message.answer("Нужно указать айди чата, например: " + md.hcode(f"/chat_info {message.chat.id}"))
        return
    db_chats = mongo.get_coll(cfg.chat_collection)
    data = await db_chats.find_one({"_id": chat_id})
    if not data:
        await message.answer("Этого чата нет в базе данных")
        return
    chat = ChatType(data)
    out = chat_formatter(chat)
    send = False
    try:
        _users = await message.bot.get_chat_members_count(chat._id)
    except Exception:
        out = "Бота удалили из чата\n"
        send = True
        _users = "???"
    out += f"Добавлен: {md.hbold(chat.reg_date.strftime('%m/%d/%Y, %H:%M:%S'))} ({humanize.precisedelta(dt.datetime.now()-chat.reg_date)})\n"
    out += f"Последнее обновление: {md.hbold(chat.last_online.strftime('%m/%d/%Y, %H:%M:%S'))}\n"
    out += f"Количество триггеров: {md.hbold(len(chat.triggers))} [{md.hlink('триггеры', f'https://t.me/share/url?url=/atriggers {chat._id}')}]\n"
    out += f"Количество людей в чате: {md.hbold(_users)}\n"
    if send:
        await message.answer(out, disable_web_page_preview=True)
        return
    _users = await message.bot.get_chat_administrators(chat._id)
    out += f"Количество админов в чате: {md.hbold(len(_users))}\n\n"
    out += "Админы в чате:\n"
    creator = None
    for index, user in enumerate(_users):
        if user.status == "administrator":
            status = "A"
        elif user.status == "creator":
            creator = user
            continue
        else:
            status = user.status
        if index >= 9:
            continue
        if not user.user.username:
            out += f"{index+1}) {user.user.get_mention(as_html=True)} - {md.hbold(status)}"
        else:
            out += f"{index+1}) {user.user.get_mention(as_html=True)} [@{user.user.username}] - {md.hbold(status)}"
        if user.custom_title:
            out += f" [{md.hbold(user.custom_title)}]"
        out += "\n"
    if creator is not None:
        if not creator.user.username:
            out += f"Создатель: {creator.user.get_mention(as_html=True)}"
        else:
            out += f"Создатель: {creator.user.get_mention(as_html=True)} [@{creator.user.username}]"
        if creator.custom_title:
            out += f" [{md.hbold(creator.custom_title)}]"
        out += "\n"
    await message.answer(out, disable_web_page_preview=True)


@dp.message_handler(
    global_admin=True,
    commands="atriggers"
)
async def atriggers(message: types.Message, mongo: FastMongo):
    chat_id = message.get_args()
    db_chats = mongo.get_coll(cfg.chat_collection)
    chat_db = await db_chats.find_one({"_id": int(chat_id)})
    if not chat_db:
        await message.answer("Такого чата не найдено")
        return
    Chat = ChatType(chat_db).to_object()
    if len(Chat.triggers) <= 0:
        out = str()
        if len(Chat.libs):
            out = "Библиотеки:\n"
            for lib_id in Chat.libs:
                db_libs = mongo.get_coll(cfg.libs_collection)
                data = await db_libs.find_one({"_id": lib_id})
                if not data:
                    continue
                lib: LibType = LibType().to_object(data)
                out += f"{lib.name} [{md.hcode(lib._id)}] - {len(lib.triggers)}\n"
        await message.answer("Триггеров ещё не создано\n" + out)
        return
    out = md.hbold("Список триггеров:\n\n")
    triggers = Chat.triggers
    lib_info = str()
    if len(Chat.libs):
        lib_info = "\nБиблиотеки:\n"
        for lib_id in Chat.libs:
            db_libs = mongo.get_coll(cfg.libs_collection)
            data = await db_libs.find_one({"_id": lib_id})
            if not data:
                continue
            lib: LibType = LibType().to_object(data)
            lib_info += f"{lib.name} [{md.hcode(lib._id)}] - {len(lib.triggers)}\n"
    counter = 25
    for trigger in triggers:
        if counter <= 0:
            await message.answer(out)
            out = str()
            counter = 25
            await sleep(cfg.GLOBAL_DELAY)
        counter -= 1
        key = trigger.command
        trigger_obj = types.Message.to_object(trigger.trigger)
        show = f"{md.hlink('S', f'https://t.me/share/url?url=/ashowtrigger {Chat._id} {trigger.trigger_id}')} "
        out += f"{md.hcode(key)} - {md.hcode(trigger_obj.content_type)} - {show}\n"
    if out != str():
        await message.answer(out + lib_info)


@dp.message_handler(
    global_admin=True,
    commands="gen_invite"
)
async def gen_invite_link(message: types.Message):
    chat_id = int(message.get_args())
    try:
        link = await message.bot.create_chat_invite_link(chat_id, member_limit=1)
        await message.answer(link.invite_link)
    except Exception:
        await message.answer("Ошибка")


@dp.message_handler(
    global_admin=True,
    commands="unban_me"
)
async def admin_unban(message: types.Message):
    chat_id = int(message.get_args())
    try:
        await message.bot.unban_chat_member(chat_id, message.from_user.id)
        await message.answer("Успех")
    except Exception:
        await message.answer("Ошибка")


@dp.message_handler(
    global_admin=True,
    commands="ashowtrigger"
)
async def ashowtrigger(message: types.Message, mongo: FastMongo):
    trigger_info = message.get_args()
    trigger_info = trigger_info.split(" ")
    db_chats = mongo.get_coll(cfg.chat_collection)
    chat_db = await db_chats.find_one({"_id": int(trigger_info[0])})
    if not chat_db:
        await message.answer("Такого чата не найдено")
        return
    Chat = ChatType(chat_db).to_object()
    for trigger in Chat.triggers:
        if trigger.trigger_id == trigger_info[1]:
            answer = types.Message.to_object(trigger.trigger)
            await answer.send_copy(message.chat.id)
            return


@dp.message_handler(
    global_admin=True,
    commands="ahelp"
)
async def ahelp(message: types.Message):
    out = ("/chats_info - Список всех чатов\n"
           "/chat_info -1234 - Инфа по конкретному чату\n"
           "/stats_lib NyaAAn - Статистика библиотеки\n"
           "/ad_active NyaAAn - Активировать рекламную кампанию\n"
           "/ad_NyaAAn - Информация о рекламной кампании\n"
           "/get_premium d/m/y - Сгенерировать премиум ключ ДО даты\n"
           "/get_codes 5 - Начать раздачу n кодов на неделю\n"
           "/get_contacts - Показать все контакты\n"
           "/msg_to -10032424 - Указать чат для общения\n"
           "/reset_talk - Сбросить чат для общения\n"
           "/graf 12h - Показать графики из графаны за n часов\n"
           "/graf 00/00/00 00:00 to 00/00/00 00:00 - Показать графики из графаны с даты до\n"
           "!bytes - Получить сообщение в байтах\n"
           "!diff (что-то) - Сравнить два сообщение, если есть аргумент, покажет изменение в байтах\n"
           "!statistic - Статистика бота\n"
           "/gen_invite -12345 - Создать ссылку на чат\n"
           "/unban_me -12345 - Разбаниться в чате")
    await message.answer(out)


@dp.message_handler(
    global_admin=True,
    is_reply=True,
    commands="del"
)
async def delcommand(message: types.Message, reply: types.Message):
    try:
        await reply.delete()
        await message.delete()
    except Exception:
        pass


@dp.message_handler(
    global_admin=True,
    commands="get_premium"
)
async def gen_premium_key(message: types.Message, mongo: FastMongo):
    date = dt.datetime.strptime(message.get_args(), "%d/%m/%y")
    if message.date > date:
        await message.answer("Сори, генерирую ключи только в будущее")
        return
    db_keys = mongo.get_coll(cfg.keys_collection)
    kid = id_gen(12)
    key = {
        "_id": kid,
        "date": date
    }
    await db_keys.insert_one(key)
    await message.answer(f"Ключ сгенерирован, чтобы его активировать, введите в чате {md.hcode(f'/premium {kid}')}")


@dp.message_handler(
    global_admin=True,
    commands="msg_to"
)
async def msg_to_chat(message: types.Message, User: UserType):
    try:
        target_chat = int(message.get_args())
    except Exception:
        await message.answer("Нужно указать айди чата")
        return
    User.fsm = "admin talk"
    User.fsm_addons = target_chat
    await User.save()
    await message.answer(f"Чат для общения установлен: {target_chat}\nЧтобы сбросить /reset_talk")


@dp.message_handler(
    global_admin=True,
    commands="reset_talk"
)
async def reset_talk(message: types.Message, User: UserType):
    await User.reset_state()
    await message.answer("Состояние сброшено")


@dp.message_handler(
    global_admin=True,
    my_state="admin talk",
    content_types=types.ContentType.ANY
)
async def talk(message: types.Message, User: UserType):
    await message.send_copy(User.fsm_addons)
    await message.reply("Сообщение отправлено")


@dp.message_handler(
    global_admin=True,
    commands="get_contacts"
)
async def get_all_contacts(message: types.Message, mongo: FastMongo):
    db_users = mongo.get_coll(cfg.user_collection)
    cursor = db_users.find({"contact": {"$ne": None}})
    users = await cursor.to_list(length=None)
    users_pages = list()
    if len(users) < 1:
        await message.answer("Контактов не найдено")
    else:
        for user in users:
            user = UserType(user)
            out = str()
            out += user_formatter(user)
            for contact in user.contact:
                user_sh: int = contact["from_user"]
                if contact["user_id"] == user_sh:
                    out += f"self ({md.hcode(contact['phone_number'])})\n"
                else:
                    user_sh = await db_users.find_one({"_id": user_sh})
                    user_sh = UserType(user_sh)
                    contact['full_name'] = contact['first_name']
                    if "last_name" in contact:
                        contact['full_name'] += ' ' + contact['last_name']
                    out += f"{md.hbold(contact['full_name'])} ({md.hcode(contact['phone_number'])})\n{user_formatter(user_sh)}\n"
            users_pages.append(out)
        for user_page in users_pages:
            await message.answer(user_page)
            await sleep(cfg.GLOBAL_DELAY)


def chat_formatter(chat: ChatType) -> str:
    out = md.hbold(chat.title)
    if chat.invite_link:
        out = md.hlink(chat.title, chat.invite_link)
    elif chat.username:
        out = md.hlink(chat.title, chat.link)
    out += f" [{md.hlink('ИНФО', f'https://t.me/share/url?url=/chat_info {chat._id}')}]\n"
    return out


def user_formatter(user: UserType) -> str:
    out = user.mention
    if user.username:
        out += md.quote_html(f" @{user.username}")
    out += f" [{md.hlink('ИНФО', f'https://t.me/share/url?url=/user_info {user._id}')}]\n"
    return out
