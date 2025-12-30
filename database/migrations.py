import asyncpg
import logging

logger = logging.getLogger(__name__)

async def apply_migrations(pool: asyncpg.Pool):
    """
    Применяет все миграции базы данных.
    """
    async with pool.acquire() as connection:
        async with connection.transaction():
            logger.info("Применение миграции: Добавление registration_date в таблицу users...")
            await connection.execute("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS registration_date DATE;
            """)
            logger.info("Миграция успешно применена.")