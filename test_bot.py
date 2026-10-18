"""
Unit tests for bot handlers including /stop command and Uzbek/English localization.
"""

import asyncio
from unittest.mock import AsyncMock
import pytest

from bot import handle_stop, session_manager, storage


def test_handle_stop_no_active_session_uzbek_default():
    async def _run():
        user_id = 999111
        message = AsyncMock()
        message.from_user.id = user_id
        bot = AsyncMock()

        # Ensure no session and default language
        session_manager.end_session(user_id)
        storage.set_user_language(user_id, "uz")

        await handle_stop(message, bot)

        message.answer.assert_called_once()
        assert "Faol test topilmadi" in message.answer.call_args[0][0]
        bot.stop_poll.assert_not_called()

    asyncio.run(_run())


def test_handle_stop_no_active_session_english():
    async def _run():
        user_id = 999112
        message = AsyncMock()
        message.from_user.id = user_id
        bot = AsyncMock()

        # Ensure no session and English language
        session_manager.end_session(user_id)
        storage.set_user_language(user_id, "en")

        await handle_stop(message, bot)

        message.answer.assert_called_once()
        assert "No active quiz session found" in message.answer.call_args[0][0]
        bot.stop_poll.assert_not_called()

    asyncio.run(_run())


def test_handle_stop_with_active_session_uzbek():
    async def _run():
        user_id = 999222
        message = AsyncMock()
        message.from_user.id = user_id
        message.chat.id = 123456
        bot = AsyncMock()

        storage.set_user_language(user_id, "uz")
        raw_questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_option_id": 0},
            {"question": "Q2", "options": ["C", "D"], "correct_option_id": 1},
        ]
        session = session_manager.create_session(user_id, 123456, raw_questions)
        session_manager.register_poll(user_id, "poll_abc", 5544)
        session.score = 1
        session.current_index = 1

        await handle_stop(message, bot)

        bot.stop_poll.assert_called_once_with(chat_id=123456, message_id=5544)
        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "Test to'xtatildi" in call_text
        assert "1 / 2 ta" in call_text
        assert "To'plangan ball:" in call_text
        assert session_manager.get_session(user_id) is None

    asyncio.run(_run())


def test_handle_stop_with_active_session_english():
    async def _run():
        user_id = 999223
        message = AsyncMock()
        message.from_user.id = user_id
        message.chat.id = 123456
        bot = AsyncMock()

        storage.set_user_language(user_id, "en")
        raw_questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_option_id": 0},
            {"question": "Q2", "options": ["C", "D"], "correct_option_id": 1},
        ]
        session = session_manager.create_session(user_id, 123456, raw_questions)
        session_manager.register_poll(user_id, "poll_abc", 5544)
        session.score = 1
        session.current_index = 1

        await handle_stop(message, bot)

        bot.stop_poll.assert_called_once_with(chat_id=123456, message_id=5544)
        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "Quiz Stopped" in call_text
        assert "1 of 2 questions" in call_text
        assert "Score so far:" in call_text
        assert session_manager.get_session(user_id) is None

    asyncio.run(_run())


def test_handle_stop_without_answered_questions():
    async def _run():
        user_id = 999333
        message = AsyncMock()
        message.from_user.id = user_id
        message.chat.id = 654321
        bot = AsyncMock()

        storage.set_user_language(user_id, "uz")
        raw_questions = [
            {"question": "Q1", "options": ["A", "B"], "correct_option_id": 0},
        ]
        session = session_manager.create_session(user_id, 654321, raw_questions)
        session_manager.register_poll(user_id, "poll_xyz", 8877)
        session.score = 0
        session.current_index = 0

        await handle_stop(message, bot)

        bot.stop_poll.assert_called_once_with(chat_id=654321, message_id=8877)
        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "Test to'xtatildi" in call_text
        assert "bekor qilindi" in call_text
        assert session_manager.get_session(user_id) is None

    asyncio.run(_run())


def test_handle_list_users_and_revoke():
    from bot import handle_list_users, handle_revoke_command
    from config import settings

    async def _run():
        admin_id = settings.ADMIN_ID or 5153693465
        settings.ADMIN_ID = admin_id
        bot = AsyncMock()

        # Non-admin cannot access
        non_admin_msg = AsyncMock()
        non_admin_msg.from_user.id = 112233
        await handle_list_users(non_admin_msg)
        non_admin_msg.answer.assert_called_with("⚠️ Only the administrator can view approved users.")

        # Admin with approved users
        target_uid = 445566
        storage.approve_user(target_uid, username="test_student", full_name="Student Test")
        admin_msg = AsyncMock()
        admin_msg.from_user.id = admin_id

        await handle_list_users(admin_msg)
        admin_msg.answer.assert_called_once()
        text = admin_msg.answer.call_args[0][0]
        assert "Tasdiqlangan foydalanuvchilar" in text or "Approved Users" in text
        assert "445566" in text

        # Revoke user via /revoke
        revoke_msg = AsyncMock()
        revoke_msg.from_user.id = admin_id
        revoke_msg.text = f"/revoke {target_uid}"

        await handle_revoke_command(revoke_msg, bot)
        revoke_msg.answer.assert_called_once()
        assert not storage.is_user_approved(target_uid, admin_id)

    asyncio.run(_run())
