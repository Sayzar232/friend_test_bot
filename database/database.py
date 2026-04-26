import asyncpg

from settings import DATABASE_URL

pool = None


async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=60,
    )

    async with pool.acquire() as connection:
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                ref_link TEXT,
                registration_date DATE,
                other_test_passed INT DEFAULT 0,
                last_reminder_kind TEXT,
                last_reminder_template TEXT,
                last_reminder_sent_at TIMESTAMP
            );
            """
        )

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tests (
                id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                num_users_passed INT DEFAULT 0,
                answers_updated_at TIMESTAMP
            );
            """
        )

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tests_answers (
                test_id BIGINT REFERENCES tests(id) ON DELETE CASCADE,
                question_index INT,
                answer TEXT,
                PRIMARY KEY (test_id, question_index)
            );
            """
        )

        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tests_results (
                id SERIAL PRIMARY KEY,
                test_id BIGINT REFERENCES tests(id) ON DELETE CASCADE,
                taker_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                score INT,
                passed_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(test_id, taker_id)
            );
            """
        )


async def add_user(user_id, ref_link, full_name, username, date):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                """
                INSERT INTO users (id, full_name, username, ref_link, registration_date, other_test_passed)
                VALUES ($1, $2, $3, $4, $5, 0)
                ON CONFLICT (id) DO NOTHING;
                """,
                user_id,
                full_name,
                username,
                ref_link,
                date,
            )
            await connection.execute(
                """
                INSERT INTO tests (id, num_users_passed, answers_updated_at)
                VALUES ($1, 0, NULL)
                ON CONFLICT (id) DO NOTHING;
                """,
                user_id,
            )


async def update_after_test_creation(user_id, data):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute("DELETE FROM tests_answers WHERE test_id = $1", user_id)

            if data and isinstance(data, list):
                insert_data = [(user_id, idx, ans) for idx, ans in enumerate(data)]
                await connection.executemany(
                    "INSERT INTO tests_answers (test_id, question_index, answer) VALUES ($1, $2, $3)",
                    insert_data,
                )

            await connection.execute(
                "UPDATE tests SET answers_updated_at = NOW() WHERE id = $1",
                user_id,
            )


async def update_after_test_completion(
    test_id,
    num_users_passed,
    best_users_passed,
    users_cant_again,
    user_id,
    other_test_passed,
    other_test_users,
    score,
):
    async with pool.acquire() as connection:
        async with connection.transaction():
            await connection.execute(
                """
                INSERT INTO tests_results (test_id, taker_id, score)
                VALUES ($1, $2, $3)
                ON CONFLICT (test_id, taker_id) DO UPDATE SET score = $3, passed_at = NOW();
                """,
                test_id,
                user_id,
                score,
            )

            await connection.execute(
                "UPDATE tests SET num_users_passed = $1 WHERE id = $2",
                num_users_passed,
                test_id,
            )

            await connection.execute(
                "UPDATE users SET other_test_passed = $1 WHERE id = $2",
                other_test_passed,
                user_id,
            )


async def get_user_data(user_id):
    async with pool.acquire() as connection:
        user_record = await connection.fetchrow(
            """
            SELECT u.full_name, u.username, u.ref_link, u.other_test_passed, u.registration_date,
                   t.num_users_passed
            FROM users u
            JOIN tests t ON u.id = t.id
            WHERE u.id = $1
            """,
            user_id,
        )

        if not user_record:
            return {
                "full_name": None,
                "username": None,
                "ref_link": None,
                "other_test_passed": 0,
                "other_test_users": {},
                "other_test_users_meta": [],
                "test_answers": [],
                "num_users_passed": 0,
                "best_users_passed": {},
                "best_users_passed_meta": [],
                "users_cant_again": [],
            }

        data = dict(user_record)

        answers_rows = await connection.fetch(
            "SELECT answer FROM tests_answers WHERE test_id = $1 ORDER BY question_index",
            user_id,
        )
        data["test_answers"] = [row["answer"] for row in answers_rows]

        results_rows = await connection.fetch(
            """
            SELECT tr.taker_id, tr.score, u.full_name, u.username
            FROM tests_results tr
            JOIN users u ON tr.taker_id = u.id
            WHERE tr.test_id = $1
            ORDER BY tr.score DESC
            """,
            user_id,
        )

        best_users_passed = {}
        best_users_passed_meta = []
        users_cant_again = []

        for row in results_rows:
            taker_id = row["taker_id"]
            uname = row.get("username") or str(taker_id)
            best_users_passed[uname] = row["score"]
            best_users_passed_meta.append(
                {
                    "user_id": taker_id,
                    "username": row.get("username"),
                    "full_name": row.get("full_name"),
                    "score": row["score"],
                }
            )
            users_cant_again.append(taker_id)

        data["best_users_passed"] = best_users_passed
        data["best_users_passed_meta"] = best_users_passed_meta
        data["users_cant_again"] = users_cant_again

        passed_tests_rows = await connection.fetch(
            """
            SELECT tr.test_id, tr.score, u.username, u.full_name
            FROM tests_results tr
            JOIN users u ON tr.test_id = u.id
            WHERE tr.taker_id = $1
            """,
            user_id,
        )
        other_test_users = {}
        other_test_users_meta = []
        for row in passed_tests_rows:
            owner_id = row["test_id"]
            owner_name = row.get("username") or str(owner_id)
            other_test_users[owner_name] = row["score"]
            other_test_users_meta.append(
                {
                    "user_id": owner_id,
                    "username": row.get("username"),
                    "full_name": row.get("full_name"),
                    "score": row["score"],
                }
            )

        data["other_test_users"] = other_test_users
        data["other_test_users_meta"] = other_test_users_meta
        data["other_test_passed"] = data.get("other_test_passed") or 0
        data["num_users_passed"] = data.get("num_users_passed") or 0

        return data


async def get_user_id_by_username(username: str) -> int | None:
    async with pool.acquire() as connection:
        user_id = await connection.fetchval(
            "SELECT id FROM users WHERE username ILIKE $1",
            username,
        )
        return user_id


async def get_users_for_weekly_reminders():
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT
                u.id,
                u.ref_link,
                u.registration_date,
                u.last_reminder_kind,
                u.last_reminder_template,
                u.last_reminder_sent_at,
                EXISTS (
                    SELECT 1
                    FROM tests_answers ta
                    WHERE ta.test_id = u.id
                ) AS has_test,
                t.answers_updated_at,
                (
                    SELECT MAX(tr.passed_at)
                    FROM tests_results tr
                    WHERE tr.test_id = u.id
                ) AS last_test_taken_at,
                (
                    SELECT MAX(tr.passed_at)
                    FROM tests_results tr
                    WHERE tr.taker_id = u.id
                ) AS last_other_test_passed_at
            FROM users u
            LEFT JOIN tests t ON t.id = u.id
            """
        )
        return [dict(row) for row in rows]


async def mark_reminder_sent(user_id: int, kind: str, template_id: str):
    async with pool.acquire() as connection:
        await connection.execute(
            """
            UPDATE users
            SET last_reminder_kind = $2,
                last_reminder_template = $3,
                last_reminder_sent_at = NOW()
            WHERE id = $1
            """,
            user_id,
            kind,
            template_id,
        )


async def get_all_user_ids():
    async with pool.acquire() as connection:
        records = await connection.fetch("SELECT id FROM users;")
        return [record["id"] for record in records]


async def get_user_count():
    async with pool.acquire() as connection:
        count = await connection.fetchval("SELECT COUNT(*) FROM users;")
        return count


async def get_total_tests_passed():
    async with pool.acquire() as connection:
        count = await connection.fetchval("SELECT COUNT(*) FROM tests_results;")
        return count or 0


async def get_last_hundred_users():
    async with pool.acquire() as connection:
        records = await connection.fetch("SELECT username FROM users ORDER BY registration_date DESC LIMIT 100;")
        if records:
            return [record["username"] for record in records]
        return []


async def get_tests_created_count():
    async with pool.acquire() as connection:
        count = await connection.fetchval("SELECT COUNT(DISTINCT test_id) FROM tests_answers;")
        return count or 0


async def get_average_test_score():
    async with pool.acquire() as connection:
        avg = await connection.fetchval("SELECT AVG(score) FROM tests_results;")
        if avg is None:
            return 0.0
        try:
            return float(avg)
        except Exception:
            return 0.0


async def get_most_common_answers_per_question(top_n: int = 1, max_questions: int = 10):
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT question_index, answer, COUNT(*) AS cnt
            FROM tests_answers
            GROUP BY question_index, answer
            ORDER BY question_index ASC, cnt DESC
            """
        )

        result = {}
        for row in rows:
            qidx = row["question_index"]
            if max_questions is not None and qidx >= max_questions:
                continue
            if qidx not in result:
                result[qidx] = []
            if len(result[qidx]) < top_n:
                result[qidx].append((row["answer"], row["cnt"]))

        return result


async def get_top_tests_by_takers(limit: int = 5):
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT t.id AS test_id, t.num_users_passed, u.username
            FROM tests t
            LEFT JOIN users u ON u.id = t.id
            ORDER BY t.num_users_passed DESC
            LIMIT $1
            """,
            limit,
        )

        return [dict(row) for row in rows]


async def close_db():
    if pool:
        await pool.close()
