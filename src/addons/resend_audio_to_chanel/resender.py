import asyncio
from collections import deque

from loguru import logger
from aiogram import types, Bot
from aiogram.types.message import ContentType
import ffmpeg
from addons.pyrogram_pytgcalls.start import RadioMesa
from pytgcalls import GroupCall

import config as cfg
from config import dp, bot

# Models
from support.models.chat import Chat
from support.models.user import User
from support.models.audio import Audio

# Repos
from support.repositories.users import UserRepository
from support.repositories.audios import AudioRepository

logger.debug("resend_audio loaded")
RADIOLIST = deque() 

async def add_new_track() -> None:
    audio = await AudioRepository().get_random()
    Bot.set_current(bot)
    url = await (await bot.get_file(audio.file_id)).get_url()
    RADIOLIST.appendleft((audio, url))

async def _change_audio(link:str) -> None:
    stream = ffmpeg.input(link)
    stream = ffmpeg.output(
        stream,
        cfg.INPUT_FILENAME,
        format='s16le',
        acodec='pcm_s16le',
        ac=2,
        ar='48k'
    ).overwrite_output()
    ffmpeg.run_async(stream)


@dp.message_handler(regexp=r"!rstop")
async def stop_radio(message: types.Message, Chat:Chat, User:User):
    GC:GroupCall = RadioMesa().get_group_call()
    await GC.stop()


@dp.message_handler(regexp=r"!rstart")
async def start_radio(message: types.Message, Chat:Chat, User:User):
    GC:GroupCall = RadioMesa().get_group_call()
    await GC.start(message.chat.id)
    GC.input_filename = cfg.INPUT_FILENAME


@dp.message_handler(content_types=ContentType.AUDIO)
async def send_audio_to_channel(message: types.Message, Chat:Chat, User:User):
    caption = [
        f"🎧 <a href ='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>"
    ]
    btn = types.InlineKeyboardMarkup()
    btn.insert(types.InlineKeyboardButton('😍', callback_data='radio_good'))
    btn.insert(types.InlineKeyboardButton('😥', callback_data='radio_bad'))

    message = await bot.send_audio(
        cfg.RADIO_CHANNEL_ID, 
        message.audio.file_id, 
        "\n".join(caption), 
        disable_notification=True,
        reply_markup=btn,
        )

    audio = Audio(
        message_id = message.message_id, 
        title = message.audio.title,
        performer = message.audio.performer,
        file_id = message.audio.file_id,
        duration = message.audio.duration,
    )
    res = await AudioRepository().create(audio)
    print(res)

@dp.callback_query_handler(chat_id = cfg.RADIO_CHANNEL_ID)
async def add_reaction(call: types.CallbackQuery, Chat:Chat, User:User):
    # TODO add vote_constraint
    btn = call.message.reply_markup.inline_keyboard[0]
    cdata = {}
    for i in btn:
        cdata[i.callback_data] = int(i["text"][0:-1] or 0)

    for i in btn:
        if call.data != i['callback_data']:
            continue
        i["text"] = f"{cdata[call.data]+1}{i['text'][-1]}"


    if (cdata["radio_bad"] - cdata["radio_good"]) >= 5:
        audio = await AudioRepository().get_by_id(id=call.message.message_id)
        audio.is_banned = True
        await AudioRepository().update(id=call.message.message_id, u=audio)
        return await call.message.delete()

    await call.message.edit_reply_markup(call.message.reply_markup)


async def _():
    await asyncio.sleep(5)
    while True:
        if len(RADIOLIST) < 3:
            await add_new_track()
            continue
        audio, url = RADIOLIST.popleft()
        audio:Audio
        await _change_audio(url)
        await asyncio.sleep(audio.duration)

loop = asyncio.get_event_loop()
loop.create_task(RadioMesa().init())
loop.create_task(_())