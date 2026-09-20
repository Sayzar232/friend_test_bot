from .database import (
    init_db,
    add_user,
    update_after_test_completion,
    update_after_test_creation,
    mark_reminder_sent,
    get_all_user_ids,
    get_average_test_score,
    get_last_hundred_users,
    get_most_common_answers_per_question,
    get_tests_created_count,
    get_top_tests_by_takers,
    get_total_tests_passed,
    get_user_count,
    get_user_data,
    get_user_id_by_username,
    get_users_for_weekly_reminders,
    close_db,
    pool
)
from .migrations import apply_migrations