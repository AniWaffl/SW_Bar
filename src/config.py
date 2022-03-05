from os import environ
from sys import stdout
from typing import Dict
from dotenv import load_dotenv
from loguru import logger
from aiogram.bot.api import TELEGRAM_PRODUCTION
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

load_dotenv()

# Prepare Logging 
logger.remove()
logger.add(stdout, colorize=True, format="<green>{time:DD.MM.YY H:mm:ss}</green> "
           "| <yellow><b>{level}</b></yellow> | <magenta>{file}</magenta> | <cyan>{message}</cyan>")

# Prepare BOT and telegram bot api server
token = environ.get("TG_TOKEN", "")

local_server = TELEGRAM_PRODUCTION
storage = MemoryStorage()

DATABASE_URL = environ.get("DATABASE", "sqlite:///test.db")

POLLING = environ.get('DEBUG', 'True').lower() == 'true'


WEBHOOK_HOST = 'localhost'
WEBHOOK_PORT = 8443
WEBHOOK_URL_PATH = "/tgbot_webhook"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL_PATH}"


allowed_updates = ["message", "callback_query", "chat_member"]
wh_max_connections = 100

admins = [int(i) for i in environ.get("ADMINS").split(",")] # Список глобальных админов

BOT_COMMANDS: Dict[str, str] = {
    "smoothie": "🧉Помощь в приготовлении смузи",
    "reflink": "Узнать id человека по рефке"
    }

bot = Bot(token=token, validate_token=True, parse_mode="HTML", server=local_server)
dp = Dispatcher(bot, run_tasks_by_default=True, storage=storage)

MAIN_CHAT_ID = int(environ.get("MAIN_CHAT_ID", -1001506010837))
SMOOTHIE_LOG_CHAT_ID = int(environ.get("SMOOTHIE_LOG_CHAT_ID", admins[0]))
SMOOTHIE_CHANNEL_ID = int(environ.get("SMOOTHIE_CHANNEL_ID", admins[0]))
# SMOOTHIE_BOT_CORP = int(environ.get("SMOOTHIE_BOT_CORP", "mesa"))
SW_BOT_ID = int(environ.get("SW_BOT_ID"))

RADIO_CHANNEL_ID = int(environ.get("RADIO_CHAT_ID", admins[0]))

# USERBOT_SESSION = str(environ.get("USERBOT_SESSION"))
# USERBOT_API_HASH = str(environ.get("USERBOT_API_HASH"))
# USERBOT_API_ID = int(environ.get("USERBOT_API_ID"))
# RADIO_PLAY_CHAT_ID = int(environ.get("RADIO_PLAY_CHAT_ID"))
# INPUT_FILENAME = 'file.raw'