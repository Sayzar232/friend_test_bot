from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os
import logging
from settings import TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET
from handlers.user_handlers import router as user_router
from handlers.callbacks_handlers import router as callbacks_router
from handlers.answers_callbacks_handlers import router as answers_callbacks_router
from handlers.message_handlers import router as states_router
from admin.admin_handlers import router as admin_router
from database.database import init_db, close_db

logging.basicConfig(
    level=logging.INFO
)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_routers(user_router, callbacks_router, states_router, admin_router, answers_callbacks_router)

async def on_startup(bot: Bot):
    try:
        await init_db()

        info = await bot.get_webhook_info()

        correct_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

        if info.url != correct_url:
            await bot.set_webhook(url=correct_url, secret_token=WEBHOOK_SECRET)
            logging.info("webhook installed")
        else:
            logging.info("webhook already set")

    except Exception as e:
        print(f"ошибка при инициализации базы данных: {e}")

async def on_shutdown(bot: Bot):
    await close_db()
    await bot.delete_webhook()

def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    port = int(os.getenv("PORT", 8080))  # берем порт, который задаёт Cloud Run
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()