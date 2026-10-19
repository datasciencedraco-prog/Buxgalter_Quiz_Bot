"""
Unit tests for storage and session management.
"""

import os
import tempfile
import pytest

from storage import StorageManager, SessionManager


@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        json_path = os.path.join(tmpdir, "allowed.json")
        sm = StorageManager(db_path=db_path, json_path=json_path)
        yield sm, json_path


def test_allowed_users_and_json_sync(temp_storage):
    sm, json_path = temp_storage
    admin_id = 999
    user_id = 12345

    assert not sm.is_user_approved(user_id, admin_id)
    assert sm.is_user_approved(admin_id, admin_id)

    sm.approve_user(user_id, username="testuser", full_name="Test User")
    assert sm.is_user_approved(user_id, admin_id)
    assert os.path.exists(json_path)

    # Verify reloading from json works
    sm2 = StorageManager(db_path=sm.db_path, json_path=json_path)
    assert sm2.is_user_approved(user_id, admin_id)


def test_question_storage_and_retrieval(temp_storage):
    sm, _ = temp_storage
    questions = [
        {"question": "Q1", "options": ["A", "B"], "correct_option_id": 0},
        {"question": "Q2", "options": ["X", "Y", "Z"], "correct_option_id": 2},
    ]
    total = sm.save_questions(questions)
    assert total == 2
    assert sm.get_questions_count() == 2

    retrieved = sm.get_all_questions()
    assert len(retrieved) == 2
    assert retrieved[0]["question"] == "Q1"
    assert retrieved[0]["options"] == ["A", "B"]
    assert retrieved[0]["correct_option_id"] == 0
    assert retrieved[1]["question"] == "Q2"
    assert retrieved[1]["correct_option_id"] == 2


def test_session_manager_shuffling_and_correct_option():
    session_mgr = SessionManager()
    user_id = 555
    chat_id = 555
    raw_questions = [
        {
            "question": f"Question {i}",
            "options": [f"Opt {i}_A", f"Opt {i}_B", f"Opt {i}_C", f"Opt {i}_D"],
            "correct_option_id": 1,  # "Opt {i}_B" is always correct
        }
        for i in range(10)
    ]

    session = session_mgr.create_session(user_id, chat_id, raw_questions)
    assert session.total_questions == 10
    assert session.current_index == 0
    assert session.score == 0

    # Verify that in every single question, correct_option_id points to the correct option text
    for q in session.questions:
        q_idx = q.question.split()[1]
        expected_text = f"Opt {q_idx}_B"
        assert q.options[q.correct_option_id] == expected_text

    # Register poll
    session_mgr.register_poll(user_id, "poll_123")
    assert session_mgr.get_session_by_poll("poll_123") == session

    # End session
    session_mgr.end_session(user_id)
    assert session_mgr.get_session(user_id) is None
    assert session_mgr.get_session_by_poll("poll_123") is None


def test_session_manager_register_poll_with_message_id():
    session_mgr = SessionManager()
    user_id = 777
    raw_questions = [{"question": "Q1", "options": ["A", "B"], "correct_option_id": 0}]
    session = session_mgr.create_session(user_id, 777, raw_questions)

    session_mgr.register_poll(user_id, "poll_xyz", 8888)
    assert session.current_poll_id == "poll_xyz"
    assert session.current_message_id == 8888
    assert session_mgr.get_session_by_poll("poll_xyz") == session

    session_mgr.end_session(user_id)
    assert session_mgr.get_session(user_id) is None
    assert session_mgr.get_session_by_poll("poll_xyz") is None


def test_user_language_settings(temp_storage):
    sm, _ = temp_storage
    user_id = 123456

    # Default should be 'uz'
    assert sm.get_user_language(user_id) == "uz"

    # Set to English
    sm.set_user_language(user_id, "en")
    assert sm.get_user_language(user_id) == "en"

    # Set back to Uzbek
    sm.set_user_language(user_id, "uz")
    assert sm.get_user_language(user_id) == "uz"

    # Invalid language falls back to 'uz'
    sm.set_user_language(user_id, "invalid")
    assert sm.get_user_language(user_id) == "uz"


def test_revoke_user_and_sync(temp_storage):
    sm, json_path = temp_storage
    admin_id = 999
    user1 = 111
    user2 = 222

    sm.approve_user(user1, username="u1", full_name="User One")
    sm.approve_user(user2, username="u2", full_name="User Two")
    assert sm.is_user_approved(user1, admin_id)
    assert sm.is_user_approved(user2, admin_id)

    all_users = sm.get_all_approved_users()
    user_ids = [u["user_id"] for u in all_users]
    assert user1 in user_ids
    assert user2 in user_ids

    # Revoke user1
    revoked = sm.revoke_user(user1)
    assert revoked is True
    assert not sm.is_user_approved(user1, admin_id)
    assert sm.is_user_approved(user2, admin_id)

    # Verify JSON file is also synced
    with open(json_path, "r", encoding="utf-8") as f:
        import json
        data = json.load(f)
        saved_ids = [item["user_id"] for item in data]
        assert user1 not in saved_ids
        assert user2 in saved_ids


def test_readonly_db_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create an existing db file and make it read-only
        ro_db = os.path.join(tmpdir, "readonly.db")
        # Initialize some data first
        sm_init = StorageManager(db_path=ro_db)
        sm_init.approve_user(777, username="lucky", full_name="Lucky")
        assert sm_init.is_user_approved(777, 999)

        # StorageManager should handle and resolve to a writable db
        sm_resolved = StorageManager(db_path=ro_db)
        # Should be able to approve another user without crashing
        sm_resolved.approve_user(888, username="worker", full_name="Worker")
        assert sm_resolved.is_user_approved(888, 999)
        assert sm_resolved.is_user_approved(777, 999)

