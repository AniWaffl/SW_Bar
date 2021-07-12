from os import environ
from sys import stdout
from typing import Dict
from loguru import logger
from aiogram.bot.api import TELEGRAM_PRODUCTION
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

print(environ)
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

# LOGGING_CHANNEL = 579287019

BOT_COMMANDS: Dict[str, str] = {
    "smoothie": "🧉Помощь в приготовлении смузи",
    }

bot = Bot(token=token, validate_token=True, parse_mode="HTML", server=local_server)
dp = Dispatcher(bot, run_tasks_by_default=True, storage=storage)

SMOOTHIE_LOG_CHAT_ID = environ.get("SMOOTHIE_LOG_CHAT_ID", admins[0])
SMOOTHIE_CHANNEL_ID = environ.get("SMOOTHIE_CHANNEL_ID", admins[0])
SW_BOT_ID = environ.get("SW_BOT_ID")