import asyncpg
from settings import DATABASE_URL
import json

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL, 
        min_size=1, 
        max_size=10,
        command_timeout=60
    )

    async with pool.acquire() as connection:
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            other_test_passed INT,
            other_test_users JSONB,
            ref_link TEXT
        );
        """)
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id BIGINT PRIMARY KEY,
            test_answers JSONB,
            num_users_passed INT,
            best_users_passed JSONB,
            users_cant_again JSONB
        );
        """)

async def add_user(user_id, ref_link, full_name, username):
    async with pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO users (id, full_name, username, ref_link, other_test_passed) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (id) DO NOTHING;",
            user_id, full_name, username, ref_link, 0
        )
        await connection.execute(
            "INSERT INTO tests (id, num_users_passed) VALUES ($1, $2) ON CONFLICT (id) DO NOTHING;",
            user_id, 0
        )

async def update_user_data(user_id, data, table_name, column_name):
    async with pool.acquire() as connection:
        await connection.execute(
            f"UPDATE {table_name} SET {column_name} = $1 WHERE id = $2;",
            json.dumps(data) if type(data) in (list, dict) else data, user_id
        )

async def update_after_test_completion(friend_id, num_users_passed, best_users_passed, users_cant_again, user_id, other_test_passed, other_test_users):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                "UPDATE tests SET num_users_passed = $1, best_users_passed = $2, users_cant_again = $3 WHERE id = $4",
                num_users_passed, json.dumps(best_users_passed), json.dumps(users_cant_again), friend_id
            )
            await connection.execute(
                "UPDATE users SET other_test_passed = $1, other_test_users = $2 WHERE id = $3",
                other_test_passed, json.dumps(other_test_users), user_id
            )

async def get_user_data(user_id):
    async with pool.acquire() as connection:
        record = await connection.fetchrow(
            """
            SELECT u.full_name, u.username, u.ref_link, u.other_test_passed, u.other_test_users, t.test_answers, t.num_users_passed, t.best_users_passed, t.users_cant_again
            FROM users u
            JOIN tests t ON u.id = t.id
            WHERE u.id = $1
            """,
            user_id
        )
        if not record:
            return None

        data = dict(record)
        if data.get('test_answers'):
            data['test_answers'] = json.loads(data['test_answers'])
        if data.get('best_users_passed'):
            data['best_users_passed'] = json.loads(data['best_users_passed'])
        if data.get('other_test_users'):
            data['other_test_users'] = json.loads(data['other_test_users'])
        if data.get('users_cant_again'):
            data['users_cant_again'] = json.loads(data['users_cant_again'])
        
        return data

async def get_all_user_ids():
    async with pool.acquire() as connection:
        records = await connection.fetch("SELECT id FROM users;")
        return [record['id'] for record in records]

async def get_user_count():
    async with pool.acquire() as connection:
        count = await connection.fetchval("SELECT COUNT(*) FROM users;")
        return count

async def get_total_tests_passed():
    async with pool.acquire() as connection:
        count = await connection.fetchval("SELECT SUM(num_users_passed) FROM tests;")
        return count or 0

async def close_db():
    if pool:
        await pool.close()
