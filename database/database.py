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
        # Таблица пользователей
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            ref_link TEXT,
            registration_date DATE,
            other_test_passed INT DEFAULT 0
        );
        """)
        
        # Таблица тестов (хранит статистику)
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS tests (
            id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            num_users_passed INT DEFAULT 0
        );
        """)
        
        # Таблица ответов на вопросы теста
        # Вместо одного JSON поля теперь строки
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS tests_answers (
            test_id BIGINT REFERENCES tests(id) ON DELETE CASCADE,
            question_index INT,
            answer TEXT,
            PRIMARY KEY (test_id, question_index)
        );
        """)
        
        # Таблица результатов (кто прошел чей тест)
        await connection.execute("""
        CREATE TABLE IF NOT EXISTS tests_results (
            id SERIAL PRIMARY KEY,
            test_id BIGINT REFERENCES tests(id) ON DELETE CASCADE,
            taker_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
            score INT,
            passed_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(test_id, taker_id)
        );
        """)

async def add_user(user_id, ref_link, full_name, username, date):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                """
                INSERT INTO users (id, full_name, username, ref_link, registration_date, other_test_passed) 
                VALUES ($1, $2, $3, $4, $5, 0) 
                ON CONFLICT (id) DO NOTHING;
                """,
                user_id, full_name, username, ref_link, date
            )
            # Создаем запись теста для пользователя (пустую)
            await connection.execute(
                "INSERT INTO tests (id, num_users_passed) VALUES ($1, 0) ON CONFLICT (id) DO NOTHING;",
                user_id
            )

async def update_after_test_creation(user_id, data):
    async with pool.acquire() as connection:
        async with connection.transaction():
            # Удаляем старые ответы
            await connection.execute("DELETE FROM tests_answers WHERE test_id = $1", user_id)
            
            # Записываем новые
            if data and isinstance(data, list):
                # Подготовим данные для bulk insert: [(test_id, index, answer), ...]
                insert_data = [(user_id, idx, ans) for idx, ans in enumerate(data)]
                await connection.executemany(
                    "INSERT INTO tests_answers (test_id, question_index, answer) VALUES ($1, $2, $3)",
                    insert_data
                )

async def update_after_test_completion(test_id, num_users_passed, best_users_passed, users_cant_again, user_id, other_test_passed, other_test_users, score):
    """
    friend_id: ID владельца теста (чьи тест прошли)
    user_id: ID того кто прошел (текущий юзер)
    """
    # Вычисляем score из best_users_passed (предполагаем, что логика передает структуру {'uid': score, ...})
    # Но лучше, если вызывающий код просто передает score. 
    # Так как сигнатуру менять не просили кардинально, попробуем извлечь score для user_id из best_users_passed
    
    async with pool.acquire() as connection:
        async with connection.transaction():
            # 1. Записываем результат прохождения
            await connection.execute(
                """
                INSERT INTO tests_results (test_id, taker_id, score) 
                VALUES ($1, $2, $3)
                ON CONFLICT (test_id, taker_id) DO UPDATE SET score = $3, passed_at = NOW();
                """,
                test_id, user_id, score
            )
            
            # 2. Обновляем счетчики (каунтеры)
            # Обновляем num_users_passed в tests
            await connection.execute(
                "UPDATE tests SET num_users_passed = $1 WHERE id = $2",
                num_users_passed, test_id
            )
            
            # Обновляем other_test_passed у того кто прошел
            await connection.execute(
                "UPDATE users SET other_test_passed = $1 WHERE id = $2",
                other_test_passed, user_id
            )

async def get_user_data(user_id):
    async with pool.acquire() as connection:
        # Получаем базовую инфу 
        user_record = await connection.fetchrow(
            """
            SELECT u.full_name, u.username, u.ref_link, u.other_test_passed, u.registration_date,
                   t.num_users_passed
            FROM users u
            JOIN tests t ON u.id = t.id
            WHERE u.id = $1
            """,
            user_id
        )
        
        if not user_record:
            return {
                'full_name': None,
                'username': None,
                'ref_link': None,
                'other_test_passed': 0,
                'other_test_users': {},
                'test_answers': [],
                'num_users_passed': 0,
                'best_users_passed': {},
                'users_cant_again': []
            }
            
        data = dict(user_record)
        
        # 1. Получаем ответы теста этого пользователя (test_answers)
        answers_rows = await connection.fetch(
            "SELECT answer FROM tests_answers WHERE test_id = $1 ORDER BY question_index",
            user_id
        )
        data['test_answers'] = [row['answer'] for row in answers_rows]
        
        # 2. Получаем список тех, кто прошел этот тест (best_users_passed и users_cant_again)
        # В старой логике это были словари/списки. Сейчас это выборка из таблицы results
        results_rows = await connection.fetch(
            """
            SELECT tr.taker_id, tr.score, u.full_name, u.username 
            FROM tests_results tr
            JOIN users u ON tr.taker_id = u.id
            WHERE tr.test_id = $1
            ORDER BY tr.score DESC
            """,
            user_id
        )
        
        # Формируем структуру как раньше, чтобы не ломать frontend/bot logic
        best_users_passed = {}
        users_cant_again = []
        
        for row in results_rows:
            # Используем username в качестве ключа для отображения в профиле
            uname = row.get('username') or str(row['taker_id'])
            best_users_passed[uname] = row['score']
            users_cant_again.append(row['taker_id'])
            
        data['best_users_passed'] = best_users_passed
        data['users_cant_again'] = users_cant_again
        
        # 3. Получаем список тестов, которые прошел ЭТОТ пользователь (other_test_users)
        # "other_test_users": {test_owner_id: score}
        passed_tests_rows = await connection.fetch(
            """
            SELECT tr.test_id, tr.score, u.username
            FROM tests_results tr
            JOIN users u ON tr.test_id = u.id
            WHERE tr.taker_id = $1
            """,
            user_id
        )
        other_test_users = {}
        for row in passed_tests_rows:
            owner_name = row.get('username') or str(row['test_id'])
            other_test_users[owner_name] = row['score']
            
        data['other_test_users'] = other_test_users

        # Гарантируем дефолтные значения
        data['other_test_passed'] = data.get('other_test_passed') or 0
        data['num_users_passed'] = data.get('num_users_passed') or 0
        
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
        # Теперь считаем реально по таблице результатов
        count = await connection.fetchval("SELECT COUNT(*) FROM tests_results;")
        return count or 0

async def get_last_hundred_users():
    async with pool.acquire() as connection:
        records = await connection.fetch("SELECT username FROM users ORDER BY registration_date DESC LIMIT 100;")
        if records:
            return [record['username'] for record in records]
        return []

async def close_db():
    if pool:
        await pool.close()
