import asyncio
from typing import Dict

from aiogram import types
from loguru import logger

import config as cfg
from main import dp

logger.debug("Setup bot commands")

async def set_default_commands(commands:Dict[str, str]):
    l = []
    for k, v in commands.items():
        l.append(types.BotCommand(k, v))

    await dp.bot.set_my_commands(l)


loop = asyncio.get_event_loop()
loop.create_task(set_default_commands(cfg.BOT_COMMANDS))