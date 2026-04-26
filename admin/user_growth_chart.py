from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from io import BytesIO


def parse_registration_date(raw_value: object) -> datetime | None:
    if raw_value is None:
        return None

    if isinstance(raw_value, datetime):
        return raw_value

    if isinstance(raw_value, date):
        return datetime.combine(raw_value, datetime.min.time())

    if isinstance(raw_value, str):
        normalized = raw_value.strip()
        if not normalized:
            return None

        normalized = normalized.replace("Z", "+00:00")

        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            for pattern in (
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d.%m.%Y %H:%M:%S",
                "%d.%m.%Y",
            ):
                try:
                    return datetime.strptime(normalized, pattern)
                except ValueError:
                    continue

    return None


async def load_daily_registrations() -> Counter[date]:
    from database.database import pool

    async with pool.acquire() as connection:
        rows = await connection.fetch(
            """
            SELECT registration_date
            FROM users
            WHERE registration_date IS NOT NULL
            """
        )

    counter: Counter[date] = Counter()
    for row in rows:
        registered_at = parse_registration_date(row["registration_date"])
        if registered_at is not None:
            counter[registered_at.date()] += 1

    return counter


def build_user_growth_chart(counter: Counter[date]) -> BytesIO:
    if not counter:
        raise ValueError("Нет данных о датах регистрации пользователей.")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dates = sorted(counter)
    values = []
    total_users = 0

    for day in dates:
        total_users += counter[day]
        values.append(total_users)

    figure, axis = plt.subplots(figsize=(12, 6))
    axis.plot(dates, values, marker="o", linewidth=2, color="#2563eb")
    axis.set_title("Рост пользователей")
    axis.set_xlabel("Дата")
    axis.set_ylabel("Всего пользователей")
    axis.grid(True, linestyle="--", alpha=0.35)
    figure.autofmt_xdate(rotation=45, ha="right")
    figure.tight_layout()

    image = BytesIO()
    figure.savefig(image, format="png", dpi=150)
    plt.close(figure)

    image.seek(0)
    return image


async def create_user_growth_chart() -> BytesIO:
    registrations = await load_daily_registrations()
    return build_user_growth_chart(registrations)
