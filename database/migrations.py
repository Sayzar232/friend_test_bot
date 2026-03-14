import asyncpg
import logging

logger = logging.getLogger(__name__)


async def apply_migrations(pool: asyncpg.Pool):
    """
    Применяет все миграции базы данных.
    """
    async with pool.acquire() as connection:
        async with connection.transaction():
            logger.info("Применение миграций базы данных...")
            await connection.execute(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS last_reminder_kind TEXT,
                ADD COLUMN IF NOT EXISTS last_reminder_template TEXT,
                ADD COLUMN IF NOT EXISTS last_reminder_sent_at TIMESTAMP;
                """
            )
            await connection.execute(
                """
                ALTER TABLE tests
                ADD COLUMN IF NOT EXISTS answers_updated_at TIMESTAMP;
                """
            )
            logger.info("Миграции успешно применены.")
