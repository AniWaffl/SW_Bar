from sys import stdout
from typing import Dict
from loguru import logger
from aiogram.bot.api import TELEGRAM_PRODUCTION
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

# Prepare Logging 
logger.remove()
logger.add(stdout, colorize=True, format="<green>{time:DD.MM.YY H:mm:ss}</green> "
           "| <yellow><b>{level}</b></yellow> | <magenta>{file}</magenta> | <cyan>{message}</cyan>")

# Prepare BOT and telegram bot api server
token = "1291948093:AAFwkk4fcJYO1fRzcM7IR3JZmV_jpvG76rY"

local_server = TELEGRAM_PRODUCTION
storage = MemoryStorage()

DATABASE_URL = "sqlite:///example.db"

POLLING = True


WEBHOOK_HOST = '193.107.128.102'
WEBHOOK_PORT = 8443
WEBHOOK_URL_PATH = "/tgbot_webhook"
WEBHOOK_URL = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_URL_PATH}"


allowed_updates = ["message", "callback_query", "chat_member"]
wh_max_connections = 100

admins = [579287019,]  # Список глобальных админов

# Prepare DBs


# Prepare scheduler NOT WORK
# SAVE_SCHEDULER = False
# executors = {DEFAULT: AsyncIOExecutor()}
# job_defaults = {"coalesce": False, "max_instances": 3}
# jobstores = {"mongo": MongoDBJobStore(database=mongo_db, collection=scheduler_collection, host=mongo_host, port=mongo_port),
#              DEFAULT: RedisJobStore(db=redis_db_jobstores,
#                                     jobs_key="trigger.jobs",
#                                     run_times_key="trigger.run_times",
#                                     host=redis_host,
#                                     port=redis_port)}


GLOBAL_DELAY = .5
TRIGGER_LOGGING = True  # Выключить, если запущен не основной бот
LOGGING_CHANNEL = 579287019

BOT_COMMANDS: Dict[str, str] = {
    "smoothie": "Помощь в приготовлении смузи",
    "gsdfgsdgsd": "sdfgsdfg sdf gsdf g",
    }

bot = Bot(token=token, validate_token=True, parse_mode="HTML", server=local_server)
dp = Dispatcher(bot, run_tasks_by_default=True, storage=storage)

SMOOTHIE_LOG_CHAT_ID = -1001357752762
SMOOTHIE_CHANNEL_ID = SMOOTHIE_LOG_CHAT_ID
SW_BOT_ID = 227859379