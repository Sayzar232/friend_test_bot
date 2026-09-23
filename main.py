import logging
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from admin import admin_router
from database import db, apply_migrations
from handlers import (
    answers_callbacks_router,
    callbacks_router,
    group_router,
    states_router,
    user_router
)
from settings import (
    PORT,
    REMINDER_TIMEZONE,
    REMINDER_WEEKDAY,
    REMINDER_HOUR,
    REMINDER_MINUTE,
    TOKEN,
    WEBHOOK_PATH,
    WEBHOOK_SECRET,
    WEBHOOK_URL
)
from utils import send_weekly_reminders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_routers(group_router, user_router, callbacks_router, states_router, admin_router, answers_callbacks_router)


async def on_startup(app):
    try:
        await db.initialize()

        await apply_migrations(db.pool)
        logger.info("База данных инициализирована")

        scheduler = AsyncIOScheduler(timezone=ZoneInfo(REMINDER_TIMEZONE))
        scheduler.add_job(
            send_weekly_reminders,
            trigger=CronTrigger(
                day_of_week=REMINDER_WEEKDAY,
                hour=REMINDER_HOUR,
                minute=REMINDER_MINUTE,
                timezone=ZoneInfo(REMINDER_TIMEZONE),
            ),
            kwargs={"bot": bot},
            id="weekly-reminders",
            replace_existing=True,
        )
        scheduler.start()
        app["scheduler"] = scheduler
        logger.info("Планировщик напоминаний запущен: раз в неделю в %02d:%02d (%s)", REMINDER_HOUR, REMINDER_MINUTE, REMINDER_TIMEZONE)

        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Старый webhook удален")

        correct_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(
            url=correct_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        logger.info("Webhook установлен: %s", correct_url)

        info = await bot.get_webhook_info()
        logger.info("Webhook info: %s", info)
    except Exception as e:
        logger.error("Ошибка при инициализации: %s", e, exc_info=True)
        raise


async def on_shutdown(app):
    try:
        scheduler = app.get("scheduler")
        if scheduler:
            scheduler.shutdown(wait=False)
            logger.info("Планировщик напоминаний остановлен")

        await db.close()
        logger.info("База данных закрыта")
    except Exception as e:
        logger.error("Ошибка при shutdown: %s", e, exc_info=True)


async def health_check(request):
    return web.Response(text="OK", status=200)


def main():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    logger.info("Запуск сервера на порту %s", PORT)
    web.run_app(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
