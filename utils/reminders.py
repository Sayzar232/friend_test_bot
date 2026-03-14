import logging
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup

from database.database import get_users_for_daily_reminders, mark_reminder_sent
from utils.keyboards import get_create_test_reminder_kb, get_share_reminder_kb

logger = logging.getLogger(__name__)

REMINDER_AFTER = timedelta(days=2)
CREATE_REMINDER_KIND = "create_test"
SHARE_REMINDER_KIND = "share_test"

CREATE_TEST_TEMPLATES = [
    (
        "create_1",
        "<b>🖐 Пора создать свой тест</b>\n\nСоздай тест о себе, чтобы узнать какой у вас уровень дружбы.",
    ),
    (
        "create_2",
        "<b>🤔 Проверь, кто знает тебя лучше всех</b>\n\nЗаполни свой тест.",
    ),
    (
        "create_3",
        "<b>😁 Тест на дружбу</b>\n\nСоздай свой тест, чтобы узнать кто лучше всего тебя знает.",
    ),
]

SHARE_TEST_TEMPLATES = [
    (
        "share_1",
        "<b>🔗 Поделись своим тестом</b>\n\nТвой тест готов! Отправь его друзьям, чтобы узнать, кто из них знает тебя лучше всех.",
    ),
    (
        "share_2",
        "<b>🤔 Давно не было результатов?</b>\n\nНапомни друзьям о своем тесте, чтобы получить новые ответы и узнать что-то интересное.",
    ),
    (
        "share_3",
        "<b>🏆 Кто твой лучший друг?</b>\n\nПоделись тестом еще раз и проверь, как хорошо тебя знают твои друзья.",
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


def _same_day(sent_at: datetime | None, current_date: date) -> bool:
    return bool(sent_at and sent_at.date() == current_date)


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
        template_id, text = _select_template(
            CREATE_REMINDER_KIND,
            candidate.last_reminder_kind,
            candidate.last_reminder_template,
        )
        return template_id, text, get_create_test_reminder_kb()

    return _build_share_payload(candidate, now)


async def send_daily_reminders(bot: Bot) -> None:
    now = datetime.now()
    candidates_raw = await get_users_for_daily_reminders()

    for raw_candidate in candidates_raw:
        candidate = _as_candidate(raw_candidate)
        if _same_day(candidate.last_reminder_sent_at, now.date()):
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
