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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_routers(user_router, callbacks_router, states_router, admin_router, answers_callbacks_router)

async def on_startup(app):
    """Инициализация при запуске"""
    try:
        await init_db()
        logger.info("База данных инициализирована")
        
        # Удаляем старый webhook перед установкой нового
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Старый webhook удален")
        
        correct_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(
            url=correct_url,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True
        )
        logger.info(f"Webhook установлен: {correct_url}")
        
        # Проверяем установку
        info = await bot.get_webhook_info()
        logger.info(f"Webhook info: {info}")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}", exc_info=True)
        raise

async def on_shutdown(app):
    """Очистка при остановке"""
    try:
        await close_db()
        logger.info("База данных закрыта")
        # НЕ удаляем webhook при shutdown в Cloud Run!
        # await bot.delete_webhook()
    except Exception as e:
        logger.error(f"Ошибка при shutdown: {e}", exc_info=True)

async def health_check(request):
    """Health check endpoint для Cloud Run"""
    return web.Response(text="OK", status=200)

def main():
    # Создаем приложение
    app = web.Application()
    
    # КРИТИЧНО: добавляем health check endpoint
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    # Регистрируем startup/shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Настраиваем webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    # Получаем порт из переменной окружения
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Запуск сервера на порту {port}")
    
    # Запускаем приложение
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()