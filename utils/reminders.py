import logging
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup

from database.database import get_users_for_weekly_reminders, mark_reminder_sent
from utils.keyboards import get_create_test_reminder_kb, get_share_reminder_kb

logger = logging.getLogger(__name__)

REMINDER_AFTER = timedelta(days=7)
REMINDER_REPEAT_AFTER = timedelta(days=7)
CREATE_REMINDER_KIND = "create_test"
SHARE_REMINDER_KIND = "share_test"

CREATE_TEST_TEMPLATES = [
    (
        "create_1",
        "Привет! Похоже, ты еще не создал свой тест.\n\nЕсли будет настроение, заполни его за пару минут - друзьям будет проще проверить, насколько хорошо они тебя знают.",
    ),
    (
        "create_2",
        "Небольшое напоминание: твой личный тест пока пуст.\n\nМожно спокойно создать его сейчас, а потом отправить ссылку друзьям.",
    ),
    (
        "create_3",
        "Загляни, когда будет удобно: твой тест еще не создан.\n\nОтветь на вопросы, и бот соберет для тебя результаты друзей.",
    ),
]

SHARE_TEST_TEMPLATES = [
    (
        "share_1",
        "Привет! Давно не было новой активности по тестам.\n\nМожешь отправить свою ссылку друзьям или пройти чей-нибудь тест, когда будет время.",
    ),
    (
        "share_2",
        "Небольшое дружеское напоминание: твой тест уже готов.\n\nЕсли хочешь обновить результаты, поделись ссылкой еще раз.",
    ),
    (
        "share_3",
        "Кажется, тесты немного застоялись.\n\nМожно позвать друзей пройти твой тест или самому ответить на тест друга.",
    ),
]


@dataclass(slots=True)
class ReminderCandidate:
    user_id: int
    ref_link: str | None
    registration_date: date | None
    has_test: bool
    answers_updated_at: datetime | None
    last_test_taken_at: datetime | None
    last_other_test_passed_at: datetime | None
    last_reminder_kind: str | None
    last_reminder_template: str | None
    last_reminder_sent_at: datetime | None


def _as_candidate(raw: dict) -> ReminderCandidate:
    return ReminderCandidate(
        user_id=raw["id"],
        ref_link=raw.get("ref_link"),
        registration_date=raw.get("registration_date"),
        has_test=bool(raw.get("has_test")),
        answers_updated_at=raw.get("answers_updated_at"),
        last_test_taken_at=raw.get("last_test_taken_at"),
        last_other_test_passed_at=raw.get("last_other_test_passed_at"),
        last_reminder_kind=raw.get("last_reminder_kind"),
        last_reminder_template=raw.get("last_reminder_template"),
        last_reminder_sent_at=raw.get("last_reminder_sent_at"),
    )


def _select_template(kind: str, last_kind: str | None, last_template: str | None) -> tuple[str, str]:
    templates = CREATE_TEST_TEMPLATES if kind == CREATE_REMINDER_KIND else SHARE_TEST_TEMPLATES
    available_templates = templates

    if last_kind == kind and last_template:
        available_templates = [item for item in templates if item[0] != last_template] or templates

    return random.choice(available_templates)


def _recently_reminded(sent_at: datetime | None, now: datetime) -> bool:
    return bool(sent_at and now - sent_at < REMINDER_REPEAT_AFTER)


def _get_base_activity_time(candidate: ReminderCandidate, now: datetime) -> datetime:
    if candidate.answers_updated_at:
        return candidate.answers_updated_at
    if candidate.registration_date:
        return datetime.combine(candidate.registration_date, time.min)
    return now


def _build_share_payload(candidate: ReminderCandidate, now: datetime) -> tuple[str, str, InlineKeyboardMarkup] | None:
    if not candidate.ref_link:
        return None

    base_activity_time = _get_base_activity_time(candidate, now)
    last_incoming_activity = candidate.last_test_taken_at or base_activity_time
    last_outgoing_activity = candidate.last_other_test_passed_at or base_activity_time

    if now - last_incoming_activity < REMINDER_AFTER and now - last_outgoing_activity < REMINDER_AFTER:
        return None

    template_id, text = _select_template(
        SHARE_REMINDER_KIND,
        candidate.last_reminder_kind,
        candidate.last_reminder_template,
    )
    return template_id, text, get_share_reminder_kb(candidate.ref_link)


def _get_reminder_payload(candidate: ReminderCandidate, now: datetime) -> tuple[str, str, InlineKeyboardMarkup] | None:
    if not candidate.has_test:
        base_activity_time = _get_base_activity_time(candidate, now)
        if now - base_activity_time < REMINDER_AFTER:
            return None

        template_id, text = _select_template(
            CREATE_REMINDER_KIND,
            candidate.last_reminder_kind,
            candidate.last_reminder_template,
        )
        return template_id, text, get_create_test_reminder_kb()

    return _build_share_payload(candidate, now)


async def send_weekly_reminders(bot: Bot) -> None:
    now = datetime.now()
    candidates_raw = await get_users_for_weekly_reminders()

    for raw_candidate in candidates_raw:
        candidate = _as_candidate(raw_candidate)
        if _recently_reminded(candidate.last_reminder_sent_at, now):
            continue

        reminder_payload = _get_reminder_payload(candidate, now)
        if reminder_payload is None:
            continue

        template_id, text, reply_markup = reminder_payload
        kind = CREATE_REMINDER_KIND if not candidate.has_test else SHARE_REMINDER_KIND

        try:
            await bot.send_message(
                chat_id=candidate.user_id,
                text=text,
                reply_markup=reply_markup,
            )
            await mark_reminder_sent(candidate.user_id, kind, template_id)
        except (TelegramForbiddenError, TelegramBadRequest):
            logger.warning("Не удалось отправить напоминание пользователю %s", candidate.user_id)
        except Exception:
            logger.exception("Ошибка при отправке напоминания пользователю %s", candidate.user_id)
