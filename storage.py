"""
Storage manager for questions, allowed users, and quiz sessions.
Supports SQLite database with automatic allowed_users.json synchronization.
"""

import json
import logging
import os
import random
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def _is_db_writable(path: str) -> bool:
    """Test if SQLite database at path can be created, opened, and written to."""
    try:
        if os.path.exists(path):
            try:
                os.chmod(path, 0o666)
            except Exception:
                pass
        else:
            parent = os.path.dirname(os.path.abspath(path)) or "."
            if not os.access(parent, os.W_OK):
                return False

        conn = sqlite3.connect(path, timeout=5.0)
        conn.execute("PRAGMA journal_mode = MEMORY;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.execute("CREATE TABLE IF NOT EXISTS _writable_test (id INTEGER PRIMARY KEY);")
        conn.execute("INSERT OR REPLACE INTO _writable_test (id) VALUES (1);")
        conn.commit()
        conn.execute("DROP TABLE IF EXISTS _writable_test;")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Database write check failed for '{path}': {e}")
        return False


def _resolve_writable_db(requested_path: str) -> str:
    """
    Ensure the database path is writable.
    If the requested path is read-only (e.g. container hosting with root-owned files),
    automatically falls back to a writable alternative while copying existing data.
    """
    if _is_db_writable(requested_path):
        return requested_path

    # Candidate 1: Try an alternate file in the same directory (owned by container user)
    parent_dir = os.path.dirname(os.path.abspath(requested_path)) or "."
    alt_name = "active_" + os.path.basename(requested_path)
    alt_path = os.path.join(parent_dir, alt_name)
    if _is_db_writable(alt_path):
        if os.path.exists(requested_path) and not os.path.exists(alt_path):
            try:
                shutil.copyfile(requested_path, alt_path)
                try:
                    os.chmod(alt_path, 0o666)
                except Exception:
                    pass
                logger.info(f"Copied read-only database '{requested_path}' to active database '{alt_path}'")
            except Exception as e:
                logger.warning(f"Failed to copy to '{alt_path}': {e}")
        return alt_path

    # Candidate 2: Fall back to temp directory (guaranteed writable in Linux/Docker containers)
    tmp_path = os.path.join(tempfile.gettempdir(), os.path.basename(requested_path))
    if os.path.exists(requested_path) and not os.path.exists(tmp_path):
        try:
            shutil.copyfile(requested_path, tmp_path)
            try:
                os.chmod(tmp_path, 0o666)
            except Exception:
                pass
            logger.info(f"Copied read-only database '{requested_path}' to writable storage '{tmp_path}'")
        except Exception as e:
            logger.warning(f"Failed to copy to '{tmp_path}': {e}")

    if _is_db_writable(tmp_path):
        return tmp_path

    return requested_path


def _resolve_writable_json(requested_path: str) -> str:
    """Ensure json_path is writable, falling back to temp directory if needed."""
    if os.path.exists(requested_path):
        try:
            os.chmod(requested_path, 0o666)
        except Exception:
            pass
        if os.access(requested_path, os.W_OK):
            return requested_path
    else:
        parent = os.path.dirname(os.path.abspath(requested_path)) or "."
        if os.access(parent, os.W_OK):
            return requested_path

    tmp_json = os.path.join(tempfile.gettempdir(), os.path.basename(requested_path))
    if os.path.exists(requested_path) and not os.path.exists(tmp_json):
        try:
            shutil.copyfile(requested_path, tmp_json)
        except Exception:
            pass
    return tmp_json


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    correct_option_id: int


@dataclass
class QuizSession:
    user_id: int
    chat_id: int
    questions: list[QuizQuestion]
    current_index: int = 0
    score: int = 0
    current_poll_id: Optional[str] = None
    current_message_id: Optional[int] = None

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> Optional[QuizQuestion]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return self.current_index >= len(self.questions)


class StorageManager:
    def __init__(self, db_path: str = "quiz_bot.db", json_path: str = "allowed_users.json"):
        self.db_path = _resolve_writable_db(db_path)
        self.json_path = _resolve_writable_json(json_path)
        self._approved_cache: Set[int] = set()
        self.init_db()
        self.load_allowed_users()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=15.0)
        conn.execute("PRAGMA journal_mode = MEMORY;")
        conn.execute("PRAGMA temp_store = MEMORY;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS allowed_users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    approved_at TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    options TEXT NOT NULL,
                    correct_option_id INTEGER NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'uz'
                )
                """
            )
            conn.commit()

    def load_allowed_users(self) -> None:
        """
        Load approved users from SQLite into in-memory cache.
        If SQLite is empty but allowed_users.json exists, import from JSON.
        """
        # Step 1: Check if allowed_users.json exists and import if needed
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        with self.get_connection() as conn:
                            cursor = conn.cursor()
                            for item in data:
                                if isinstance(item, dict) and "user_id" in item:
                                    cursor.execute(
                                        """
                                        INSERT OR IGNORE INTO allowed_users (user_id, username, full_name, approved_at)
                                        VALUES (?, ?, ?, ?)
                                        """,
                                        (
                                            item["user_id"],
                                            item.get("username", ""),
                                            item.get("full_name", ""),
                                            item.get("approved_at", datetime.now().isoformat()),
                                        ),
                                    )
                                elif isinstance(item, int):
                                    cursor.execute(
                                        """
                                        INSERT OR IGNORE INTO allowed_users (user_id, username, full_name, approved_at)
                                        VALUES (?, ?, ?, ?)
                                        """,
                                        (item, "", "", datetime.now().isoformat()),
                                    )
                            conn.commit()
            except Exception as e:
                logger.error(f"Error loading {self.json_path}: {e}")

        # Step 2: Populate cache from database
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM allowed_users")
            rows = cursor.fetchall()
            self._approved_cache = {row["user_id"] for row in rows}

        self.sync_json()

    def sync_json(self) -> None:
        """Synchronize the allowed_users table to allowed_users.json."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, username, full_name, approved_at FROM allowed_users")
                rows = [dict(row) for row in cursor.fetchall()]

            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to sync {self.json_path}: {e}")

    def is_user_approved(self, user_id: int, admin_id: int) -> bool:
        """Check if user is admin or in approved users list."""
        if user_id == admin_id:
            return True
        return user_id in self._approved_cache

    def approve_user(self, user_id: int, username: str = "", full_name: str = "") -> None:
        """Add user to approved list and persist across DB and JSON."""
        approved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO allowed_users (user_id, username, full_name, approved_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, username, full_name, approved_at),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error persisting approved user {user_id} to database: {e}")
        self._approved_cache.add(user_id)
        self.sync_json()

    def get_all_approved_users(self) -> list[dict]:
        """Fetch all approved users from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, username, full_name, approved_at FROM allowed_users ORDER BY approved_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def revoke_user(self, user_id: int) -> bool:
        """Remove user from approved list and sync DB, cache, and JSON."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM allowed_users WHERE user_id = ?", (user_id,))
            deleted = cursor.rowcount > 0
            conn.commit()

        self._approved_cache.discard(user_id)
        self.sync_json()
        return deleted

    def save_questions(self, questions: list[dict], replace: bool = True) -> int:
        """
        Save parsed questions to database.
        Returns total number of questions currently stored.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if replace:
                cursor.execute("DELETE FROM questions")

            for q in questions:
                cursor.execute(
                    """
                    INSERT INTO questions (question, options, correct_option_id)
                    VALUES (?, ?, ?)
                    """,
                    (
                        q["question"],
                        json.dumps(q["options"], ensure_ascii=False),
                        q["correct_option_id"],
                    ),
                )
            conn.commit()

            cursor.execute("SELECT COUNT(*) FROM questions")
            total = cursor.fetchone()[0]
            return total

    def get_all_questions(self) -> list[dict]:
        """Fetch all questions from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, options, correct_option_id FROM questions")
            rows = cursor.fetchall()
            questions = []
            for row in rows:
                questions.append(
                    {
                        "id": row["id"],
                        "question": row["question"],
                        "options": json.loads(row["options"]),
                        "correct_option_id": row["correct_option_id"],
                    }
                )
            return questions

    def get_questions_count(self) -> int:
        """Return total number of questions stored."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM questions")
            return cursor.fetchone()[0]

    def get_user_language(self, user_id: int) -> str:
        """Get user preferred language. Defaults to 'uz'."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT language FROM user_settings WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row and row["language"]:
                return row["language"]
        return "uz"

    def set_user_language(self, user_id: int, language: str) -> None:
        """Set user preferred language ('uz' or 'en')."""
        if language not in ("uz", "en"):
            language = "uz"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_settings (user_id, language)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
                """,
                (user_id, language),
            )
            conn.commit()


class SessionManager:
    """Manages active interactive quiz sessions for users."""

    def __init__(self):
        self._sessions: dict[int, QuizSession] = {}
        self._poll_to_user: dict[str, int] = {}

    def create_session(self, user_id: int, chat_id: int, raw_questions: list[dict]) -> QuizSession:
        """
        Create a new randomized quiz session for a user.
        1. Shuffles question order.
        2. Shuffles options within each question and tracks correct index.
        """
        # Cleanup any previous active polls for this user
        self.end_session(user_id)

        questions_copy = list(raw_questions)
        random.shuffle(questions_copy)

        prepared: list[QuizQuestion] = []
        for q in questions_copy:
            orig_options = q["options"]
            orig_correct_id = q["correct_option_id"]
            correct_text = orig_options[orig_correct_id]

            shuffled_options = list(orig_options)
            random.shuffle(shuffled_options)
            new_correct_id = shuffled_options.index(correct_text)

            prepared.append(
                QuizQuestion(
                    question=q["question"],
                    options=shuffled_options,
                    correct_option_id=new_correct_id,
                )
            )

        session = QuizSession(
            user_id=user_id,
            chat_id=chat_id,
            questions=prepared,
            current_index=0,
            score=0,
            current_poll_id=None,
        )
        self._sessions[user_id] = session
        return session

    def register_poll(self, user_id: int, poll_id: str, message_id: Optional[int] = None) -> None:
        """Register the active poll ID and message ID for a user's session."""
        session = self._sessions.get(user_id)
        if session:
            session.current_poll_id = poll_id
            session.current_message_id = message_id
            self._poll_to_user[poll_id] = user_id

    def get_session_by_poll(self, poll_id: str) -> Optional[QuizSession]:
        """Lookup session by poll ID."""
        user_id = self._poll_to_user.get(poll_id)
        if user_id is not None:
            return self._sessions.get(user_id)
        return None

    def get_session(self, user_id: int) -> Optional[QuizSession]:
        """Lookup session by user ID."""
        return self._sessions.get(user_id)

    def end_session(self, user_id: int) -> None:
        """Clean up active session and poll references."""
        session = self._sessions.pop(user_id, None)
        if session and session.current_poll_id:
            self._poll_to_user.pop(session.current_poll_id, None)
