from aiogram import executor, types, exceptions
from aiogram.contrib.middlewares import logging
from aiogram.dispatcher.webhook import configure_app
from aiohttp import web
from aiohttp.web_app import Application
from loguru import logger
import config as cfg
from config import bot, dp

# Create database tables
import support.db

# Models
from support.models.chat import Chat
from support.repositories.chats import ChatRepository 

# Activate all modules
import addons


logging_middleware = logging.LoggingMiddleware()
logging_middleware.logger = logger
dp.middleware.setup(logging_middleware)  # ALL LOGGING
from support.usermiddleware import UserMiddleware
dp.middleware.setup(UserMiddleware())  # Мидлварь для паттернов
from support.throttlingmiddleware import ThrottlingMiddleware
dp.middleware.setup(ThrottlingMiddleware(limit=.6))  # Мидлварь для троттлинга


@dp.errors_handler(run_task=True)
async def errors(update: types.Update, error: Exception):
    if isinstance(error, exceptions.BadRequest):
        if error.args and "no rights to send" in error.args[0]:
            msg = update.message or update.callback_query.message
            await msg.chat.leave()
            return True
    logger.warning(update)
    try:
        raise error
    except Exception:
        logger.exception("Ooops")
    return True



@dp.message_handler(content_types=types.ContentTypes.MIGRATE_FROM_CHAT_ID)
async def migrate_group_to_supergroup(message: types.Message, Chat: Chat):
    """
    Миграция группы до супергруппы
    message.migrate_from_chat_id - Предыдущий айди
    message.chat.id - Новый айди
    """
    repo = ChatRepository()
    await repo.delete(message.migrate_from_chat_id)
    Chat.id = message.chat.id
    await repo.update(message.chat.id, Chat)
    logger.info(f"Группа {message.migrate_from_chat_id} обновилась до супергруппы {message.chat.id}")




@dp.callback_query_handler(text="delete-keyboard")
async def delete_callback(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.answer()


@dp.callback_query_handler()
async def any_callback(call: types.CallbackQuery):
    await call.answer("🛑🛑🛑", show_alert=True)


async def proceed_telegram_update(req: web.Request):
    upds = [types.Update(**(await req.json()))]
    bot.set_current(bot)
    await dp.process_updates(upds)
    return web.Response(status=200)


async def on_startup(app: Application):
    botinfo = await dp.bot.me
    if not cfg.POLLING:
        logger.debug(f"Устанавливаю вебхук {cfg.WEBHOOK_URL}")
        await bot.set_webhook(cfg.WEBHOOK_URL,
                              allowed_updates=cfg.allowed_updates,
                              drop_pending_updates=True,
                              max_connections=cfg.wh_max_connections)
    logger.info(f"Бот {botinfo.full_name} [@{botinfo.username}] запущен")


async def on_shutdown(app: Application):
    logger.warning('Выключаюсь..')
    if not cfg.POLLING:
        await bot.delete_webhook(drop_pending_updates=True)
    await bot.close()


if __name__ == "__main__":
    if cfg.POLLING:
        executor.start_polling(dp,
                               on_startup=on_startup,
                               on_shutdown=on_shutdown,
                               allowed_updates=cfg.allowed_updates,
                               skip_updates=True
                               )
    else:
        app = web.Application()
        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)
        configure_app(dp, app, path=cfg.WEBHOOK_PATH)
        web.run_app(app, port=cfg.WEBHOOK_PORT, host=cfg.WEBHOOK_HOST)
