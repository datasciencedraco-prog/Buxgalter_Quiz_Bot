"""
Telegram Quiz Bot handlers, router configuration, and poll listeners using aiogram v3.
Supports Uzbek (default) and English interface languages.
"""

import asyncio
import io
import logging
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import settings
from locales import get_lang_display, get_text
from parser import parse_docx
from storage import SessionManager, StorageManager

logger = logging.getLogger(__name__)

router = Router(name="quiz_router")
storage = StorageManager(db_path=settings.DATABASE_PATH, json_path=settings.ALLOWED_USERS_FILE)
session_manager = SessionManager()


def get_main_keyboard(lang: str = "uz", is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Persistent reply keyboard with quick actions in user's language."""
    bottom_row = [
        KeyboardButton(text=get_text("kb_users", lang)),
        KeyboardButton(text=get_text("kb_lang", lang)),
    ] if is_admin else [
        KeyboardButton(text=get_text("kb_lang", lang)),
    ]
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("kb_quiz", lang)),
                KeyboardButton(text=get_text("kb_stop", lang)),
            ],
            [
                KeyboardButton(text=get_text("kb_stats", lang)),
                KeyboardButton(text=get_text("kb_help", lang)),
            ],
            bottom_row,
        ],
        resize_keyboard=True,
    )


def get_request_access_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("btn_request_access", lang), callback_data="request_access")]
        ]
    )


def get_approval_kb(user_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("btn_approve", lang), callback_data=f"approve:{user_id}"),
                InlineKeyboardButton(text=get_text("btn_reject", lang), callback_data=f"reject:{user_id}"),
            ]
        ]
    )


def get_language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang:uz"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en"),
            ]
        ]
    )


@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot):
    """Handle /start command. Check access permission and present appropriate UI."""
    user = message.from_user
    if not user:
        return

    user_id = user.id
    lang = storage.get_user_language(user_id)
    is_approved = storage.is_user_approved(user_id, settings.ADMIN_ID)

    if is_approved:
        is_admin = (user_id == settings.ADMIN_ID)
        admin_note = get_text("admin_note", lang) if is_admin else ""
        text = get_text("welcome_approved", lang, name=user.first_name) + admin_note
        await message.answer(
            text,
            reply_markup=get_main_keyboard(lang, is_admin=is_admin),
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            get_text("welcome_restricted", lang),
            reply_markup=get_request_access_kb(lang),
            parse_mode=ParseMode.HTML,
        )


@router.message(Command("lang", "language"))
@router.message(F.text.in_(["🌐 Tilni almashtirish", "🌐 Change Language", "🌐 Til / Language"]))
async def handle_lang_command(message: types.Message):
    """Present language selection menu."""
    user_id = message.from_user.id if message.from_user else 0
    lang = storage.get_user_language(user_id)
    await message.answer(
        get_text("choose_lang", lang),
        reply_markup=get_language_kb(),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def handle_set_language(callback: types.CallbackQuery):
    """Handle user language selection."""
    user = callback.from_user
    if not user:
        return

    user_id = user.id
    parts = callback.data.split(":")
    lang = parts[1] if len(parts) > 1 else "uz"
    storage.set_user_language(user_id, lang)

    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            get_text("lang_changed", lang),
            parse_mode=ParseMode.HTML,
        )
        if storage.is_user_approved(user_id, settings.ADMIN_ID):
            is_admin = (user_id == settings.ADMIN_ID)
            await callback.message.answer(
                get_text("welcome_approved", lang, name=user.first_name),
                reply_markup=get_main_keyboard(lang, is_admin=is_admin),
                parse_mode=ParseMode.HTML,
            )


@router.message(Command("help"))
@router.message(F.text.in_(["📖 Yo'riqnoma", "📖 Help"]))
async def handle_help(message: types.Message):
    """Display help information."""
    user_id = message.from_user.id if message.from_user else 0
    lang = storage.get_user_language(user_id)
    await message.answer(
        get_text("help_text", lang),
        reply_markup=get_main_keyboard(lang),
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("stats"))
@router.message(F.text.in_(["📊 Statistika", "📊 Statistics"]))
async def handle_stats(message: types.Message):
    """Display current statistics."""
    count = storage.get_questions_count()
    user_id = message.from_user.id if message.from_user else 0
    lang = storage.get_user_language(user_id)
    is_approved = storage.is_user_approved(user_id, settings.ADMIN_ID)
    status_str = get_text("status_approved", lang) if is_approved else get_text("status_pending", lang)

    await message.answer(
        get_text("stats_text", lang, count=count, status=status_str, lang_name=get_lang_display(lang)),
        reply_markup=get_main_keyboard(lang),
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data == "request_access")
async def handle_request_access(callback: types.CallbackQuery, bot: Bot):
    """Handle access request button click."""
    user = callback.from_user
    if not user:
        return

    user_id = user.id
    lang = storage.get_user_language(user_id)
    if storage.is_user_approved(user_id, settings.ADMIN_ID):
        await callback.answer(get_text("already_approved", lang), show_alert=True)
        return

    full_name = user.full_name or "Unknown"
    username = f"@{user.username}" if user.username else "None"

    # Alert the admin
    if settings.ADMIN_ID:
        try:
            admin_lang = storage.get_user_language(settings.ADMIN_ID)
            await bot.send_message(
                chat_id=settings.ADMIN_ID,
                text=get_text(
                    "admin_request_title",
                    admin_lang,
                    full_name=full_name,
                    username=username,
                    user_id=user_id,
                ),
                reply_markup=get_approval_kb(user_id, admin_lang),
                parse_mode=ParseMode.HTML,
            )
            if callback.message:
                await callback.message.edit_text(
                    get_text("request_submitted", lang),
                    parse_mode=ParseMode.HTML,
                )
            await callback.answer(get_text("request_sent_toast", lang))
            return
        except Exception as e:
            logger.error(f"Failed to notify admin {settings.ADMIN_ID}: {e}")

    await callback.answer(get_text("admin_error_toast", lang), show_alert=True)


@router.callback_query(F.data.startswith("approve:"))
async def handle_approve_user(callback: types.CallbackQuery, bot: Bot):
    """Handle admin clicking Approve button."""
    if not callback.from_user or callback.from_user.id != settings.ADMIN_ID:
        admin_lang = storage.get_user_language(callback.from_user.id if callback.from_user else 0)
        await callback.answer(get_text("access_denied_admin", admin_lang), show_alert=True)
        return

    parts = callback.data.split(":")
    if len(parts) != 2:
        return

    target_user_id = int(parts[1])
    storage.approve_user(target_user_id)
    admin_lang = storage.get_user_language(settings.ADMIN_ID)

    if callback.message:
        orig = callback.message.html_text or ""
        label = get_text("admin_approved_label", admin_lang)
        await callback.message.edit_text(
            f"{orig}\n\n{label}",
            reply_markup=None,
            parse_mode=ParseMode.HTML,
        )

    await callback.answer("OK")

    # Notify the user directly in user's language
    try:
        user_lang = storage.get_user_language(target_user_id)
        await bot.send_message(
            chat_id=target_user_id,
            text=get_text("user_approved_notice", user_lang),
            reply_markup=get_main_keyboard(user_lang),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.warning(f"Could not notify approved user {target_user_id}: {e}")


@router.callback_query(F.data.startswith("reject:"))
async def handle_reject_user(callback: types.CallbackQuery, bot: Bot):
    """Handle admin clicking Reject button."""
    if not callback.from_user or callback.from_user.id != settings.ADMIN_ID:
        admin_lang = storage.get_user_language(callback.from_user.id if callback.from_user else 0)
        await callback.answer(get_text("access_denied_admin", admin_lang), show_alert=True)
        return

    parts = callback.data.split(":")
    if len(parts) != 2:
        return

    target_user_id = int(parts[1])
    admin_lang = storage.get_user_language(settings.ADMIN_ID)

    if callback.message:
        orig = callback.message.html_text or ""
        label = get_text("admin_rejected_label", admin_lang)
        await callback.message.edit_text(
            f"{orig}\n\n{label}",
            reply_markup=None,
            parse_mode=ParseMode.HTML,
        )

    await callback.answer("OK")

    # Notify user directly in user's language
    try:
        user_lang = storage.get_user_language(target_user_id)
        await bot.send_message(
            chat_id=target_user_id,
            text=get_text("user_rejected_notice", user_lang),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.warning(f"Could not notify rejected user {target_user_id}: {e}")


@router.message(Command("quiz"))
@router.message(F.text.in_(["🎯 Testni boshlash", "🎯 Start Quiz"]))
async def handle_quiz(message: types.Message, bot: Bot):
    """Start a randomized quiz session for approved user."""
    user = message.from_user
    if not user:
        return

    user_id = user.id
    lang = storage.get_user_language(user_id)
    if not storage.is_user_approved(user_id, settings.ADMIN_ID):
        await message.answer(
            get_text("quiz_denied", lang),
            reply_markup=get_request_access_kb(lang),
            parse_mode=ParseMode.HTML,
        )
        return

    questions = storage.get_all_questions()
    if not questions:
        await message.answer(
            get_text("bank_empty", lang),
            parse_mode=ParseMode.HTML,
        )
        return

    # Create new randomized session
    session = session_manager.create_session(user_id, message.chat.id, questions)
    first_q = session.current_question
    if not first_q:
        return

    await message.answer(
        get_text("quiz_started", lang, total=session.total_questions),
        reply_markup=get_main_keyboard(lang),
        parse_mode=ParseMode.HTML,
    )

    q_title = f"[{session.current_index + 1}/{session.total_questions}] {first_q.question}"
    if len(q_title) > 300:
        q_title = q_title[:297] + "..."

    poll_msg = await bot.send_poll(
        chat_id=message.chat.id,
        question=q_title,
        options=first_q.options,
        type="quiz",
        correct_option_id=first_q.correct_option_id,
        is_anonymous=False,
    )
    session_manager.register_poll(user_id, poll_msg.poll.id, poll_msg.message_id)


@router.message(Command("stop"))
@router.message(F.text.in_(["🛑 To'xtatish", "🛑 Stop Quiz", "🛑 Testni to'xtatish"]))
async def handle_stop(message: types.Message, bot: Bot):
    """Stop the user's active quiz session."""
    user = message.from_user
    if not user:
        return

    user_id = user.id
    lang = storage.get_user_language(user_id)
    session = session_manager.get_session(user_id)
    if not session:
        await message.answer(
            get_text("stop_no_session", lang),
            reply_markup=get_main_keyboard(lang),
            parse_mode=ParseMode.HTML,
        )
        return

    # Attempt to close active poll message if present
    if session.current_message_id:
        try:
            await bot.stop_poll(chat_id=session.chat_id, message_id=session.current_message_id)
        except Exception as e:
            logger.debug(f"Could not stop poll {session.current_message_id}: {e}")

    answered = session.current_index
    total = session.total_questions
    score = session.score
    session_manager.end_session(user_id)

    if answered > 0:
        pct = (score / answered * 100) if answered > 0 else 0
        await message.answer(
            get_text("stop_with_score", lang, answered=answered, total=total, score=score, pct=pct),
            reply_markup=get_main_keyboard(lang),
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            get_text("stop_cancelled", lang),
            reply_markup=get_main_keyboard(lang),
            parse_mode=ParseMode.HTML,
        )


@router.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer, bot: Bot):
    """
    Handle poll answers in real-time.
    Score computation, advancement to next question, and final results.
    """
    poll_id = poll_answer.poll_id
    user = poll_answer.user
    if not user:
        return

    user_id = user.id
    session = session_manager.get_session_by_poll(poll_id)
    if not session or session.user_id != user_id:
        return

    current_q = session.current_question
    if current_q and poll_answer.option_ids:
        user_selected = poll_answer.option_ids[0]
        if user_selected == current_q.correct_option_id:
            session.score += 1

    # Advance to next question
    session.current_index += 1

    # Allow 1.2s delay for Telegram's native correct/wrong answer visual feedback
    await asyncio.sleep(1.2)

    if session.is_finished:
        total = session.total_questions
        score = session.score
        pct = (score / total * 100) if total > 0 else 0
        lang = storage.get_user_language(user_id)

        await bot.send_message(
            chat_id=session.chat_id,
            text=get_text("quiz_completed", lang, score=score, total=total, pct=pct),
            reply_markup=get_main_keyboard(lang),
            parse_mode=ParseMode.HTML,
        )
        session_manager.end_session(user_id)
    else:
        next_q = session.current_question
        if not next_q:
            return

        q_title = f"[{session.current_index + 1}/{session.total_questions}] {next_q.question}"
        if len(q_title) > 300:
            q_title = q_title[:297] + "..."

        poll_msg = await bot.send_poll(
            chat_id=session.chat_id,
            question=q_title,
            options=next_q.options,
            type="quiz",
            correct_option_id=next_q.correct_option_id,
            is_anonymous=False,
        )
        session_manager.register_poll(user_id, poll_msg.poll.id, poll_msg.message_id)


@router.message(F.document)
async def handle_document_upload(message: types.Message, bot: Bot):
    """
    Handle .docx question file upload from the administrator.
    Downloads, parses, and loads questions into database.
    """
    user = message.from_user
    lang = storage.get_user_language(user.id if user else 0)

    if not user or user.id != settings.ADMIN_ID:
        await message.answer(get_text("doc_admin_only", lang))
        return

    doc = message.document
    if not doc or not doc.file_name or not doc.file_name.lower().endswith(".docx"):
        await message.answer(
            get_text("doc_invalid_ext", lang),
            parse_mode=ParseMode.HTML,
        )
        return

    status_msg = await message.answer(
        get_text("doc_ingesting", lang, filename=doc.file_name),
        parse_mode=ParseMode.HTML,
    )

    try:
        file_stream = io.BytesIO()
        await bot.download(doc, destination=file_stream)
        file_stream.seek(0)

        questions = parse_docx(file_stream)
        if not questions:
            await status_msg.edit_text(
                get_text("doc_no_questions", lang, filename=doc.file_name),
                parse_mode=ParseMode.HTML,
            )
            return

        total_in_db = storage.save_questions(questions, replace=True)
        await status_msg.edit_text(
            get_text("doc_success", lang, filename=doc.file_name, parsed=len(questions), total=total_in_db),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.exception("Error ingesting docx file")
        await status_msg.edit_text(f"❌ Error during file ingestion: {e}")


@router.message(Command("users"))
@router.message(F.text.in_(["👥 Foydalanuvchilar", "👥 Users"]))
async def handle_list_users(message: types.Message):
    """(Admin only) View all approved users with buttons to revoke access."""
    user = message.from_user
    if not user or user.id != settings.ADMIN_ID:
        await message.answer("⚠️ Only the administrator can view approved users.")
        return

    lang = storage.get_user_language(user.id)
    all_users = storage.get_all_approved_users()
    non_admin_users = [u for u in all_users if u["user_id"] != settings.ADMIN_ID]

    if not non_admin_users:
        await message.answer(
            get_text("no_other_users", lang),
            parse_mode=ParseMode.HTML,
        )
        return

    lines = [get_text("users_title", lang, total=len(non_admin_users))]
    buttons = []
    for idx, u in enumerate(non_admin_users, start=1):
        name = u["full_name"] or u["username"] or str(u["user_id"])
        username = f" (@{u['username']})" if u["username"] else ""
        lines.append(
            f"<b>{idx}. {name}{username}</b>\n"
            f"   🆔 ID: <code>{u['user_id']}</code>\n"
            f"   📅 Sana: <i>{u.get('approved_at', '-')}</i>"
        )
        short_name = name[:14]
        buttons.append([
            InlineKeyboardButton(
                text=get_text("btn_revoke_user", lang, name=short_name, uid=u["user_id"]),
                callback_data=f"revoke:{u['user_id']}",
            )
        ])

    lines.append(get_text("revoke_usage", lang))
    kb = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

    await message.answer("\n\n".join(lines), reply_markup=kb, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("revoke:"))
async def handle_revoke_callback(callback: types.CallbackQuery, bot: Bot):
    """(Admin only) Revoke user access via inline button."""
    admin = callback.from_user
    if not admin or admin.id != settings.ADMIN_ID:
        await callback.answer("Access denied. Admin only.", show_alert=True)
        return

    parts = callback.data.split(":")
    if len(parts) != 2:
        return
    try:
        target_uid = int(parts[1])
    except ValueError:
        return

    lang = storage.get_user_language(admin.id)
    if target_uid == settings.ADMIN_ID:
        await callback.answer(get_text("cannot_revoke_admin", lang), show_alert=True)
        return

    storage.revoke_user(target_uid)
    session_manager.end_session(target_uid)

    await callback.answer()
    if callback.message:
        await callback.message.edit_text(
            get_text("user_revoked_success", lang, uid=target_uid),
            parse_mode=ParseMode.HTML,
        )

    # Notify revoked user
    try:
        target_lang = storage.get_user_language(target_uid)
        await bot.send_message(
            chat_id=target_uid,
            text=get_text("user_revoked_alert", target_lang),
            reply_markup=get_request_access_kb(target_lang),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.debug(f"Could not notify revoked user {target_uid}: {e}")


@router.message(Command("revoke"))
async def handle_revoke_command(message: types.Message, bot: Bot):
    """(Admin only) Revoke user access via command: /revoke <user_id>."""
    user = message.from_user
    if not user or user.id != settings.ADMIN_ID:
        await message.answer("⚠️ Only the administrator can revoke users.")
        return

    lang = storage.get_user_language(user.id)
    parts = (message.text or "").strip().split()
    if len(parts) < 2:
        await message.answer(
            "⚠️ Foydalanish: <code>/revoke [ID]</code>\nMasalan: <code>/revoke 123456789</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        target_uid = int(parts[1])
    except ValueError:
        await message.answer("⚠️ Noto'g'ri ID ko'rsatildi.")
        return

    if target_uid == settings.ADMIN_ID:
        await message.answer(get_text("cannot_revoke_admin", lang))
        return

    deleted = storage.revoke_user(target_uid)
    if not deleted:
        await message.answer(get_text("user_not_found", lang))
        return

    session_manager.end_session(target_uid)
    await message.answer(
        get_text("user_revoked_success", lang, uid=target_uid),
        parse_mode=ParseMode.HTML,
    )

    try:
        target_lang = storage.get_user_language(target_uid)
        await bot.send_message(
            chat_id=target_uid,
            text=get_text("user_revoked_alert", target_lang),
            reply_markup=get_request_access_kb(target_lang),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.debug(f"Could not notify revoked user {target_uid}: {e}")
