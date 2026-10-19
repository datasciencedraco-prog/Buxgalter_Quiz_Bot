"""
Main application entry point.
Initializes aiogram Bot, Dispatcher, and starts long-polling.
"""

import asyncio
import logging
import os
import sys

# Self-contained dependency bootstrap for containerized hosting environments (WispByte, Pterodactyl, etc.)
PACKAGES_DIR = "/tmp/packages"
if os.path.exists(PACKAGES_DIR) and PACKAGES_DIR not in sys.path:
    sys.path.insert(0, PACKAGES_DIR)

try:
    import aiogram
    import docx
    import pydantic_settings
except ImportError:
    import subprocess
    print("[BOOTSTRAP] Missing dependencies detected. Installing to /tmp/packages...")
    os.makedirs(PACKAGES_DIR, exist_ok=True)
    if PACKAGES_DIR not in sys.path:
        sys.path.insert(0, PACKAGES_DIR)
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--target",
        PACKAGES_DIR,
        "--no-cache-dir",
        "aiogram>=3.4.0",
        "python-docx>=1.1.0",
        "pydantic-settings>=2.2.0",
    ])
    print("[BOOTSTRAP] Dependencies successfully installed!")

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot import router, storage
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN.startswith("123456789:ABC"):
        logger.error(
            "BOT_TOKEN is not configured! Please configure a valid BOT_TOKEN in .env file."
        )
        print("\n[ERROR] BOT_TOKEN is missing or placeholder.")
        print("Please copy .env.example to .env and provide your BOT_TOKEN and ADMIN_ID.\n")
        return

    if not settings.ADMIN_ID:
        logger.warning(
            "ADMIN_ID is 0! Admin functionality and access approvals will be disabled."
        )

    logger.info("Initializing Bot and Dispatcher...")
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    # Automatically ensure ADMIN_ID is in approved users if configured
    if settings.ADMIN_ID:
        try:
            storage.approve_user(settings.ADMIN_ID, username="admin", full_name="Bot Administrator")
        except Exception as e:
            logger.error(f"Failed to auto-approve admin {settings.ADMIN_ID}: {e}")

    # If question bank is empty and sample_quiz.docx exists, auto-load questions
    try:
        if storage.get_questions_count() == 0 and os.path.exists("sample_quiz.docx"):
            from parser import parse_docx
            logger.info("Question bank is empty. Auto-loading questions from sample_quiz.docx...")
            doc_questions = parse_docx("sample_quiz.docx")
            if doc_questions:
                storage.save_questions(doc_questions)
                logger.info(f"Loaded {len(doc_questions)} questions from sample_quiz.docx.")
    except Exception as e:
        logger.warning(f"Could not auto-populate questions from sample_quiz.docx: {e}")

    logger.info(f"Bot started. Question bank count: {storage.get_questions_count()}")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        # Register default commands in Uzbek
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Asosiy menyu va tekshirish"),
                BotCommand(command="quiz", description="Testni boshlash"),
                BotCommand(command="stop", description="Testni to'xtatish"),
                BotCommand(command="stats", description="Savollar statistikasi"),
                BotCommand(command="help", description="Qo'llanma va yordam"),
                BotCommand(command="lang", description="Tilni tanlash / Language"),
            ]
        )
        # Register commands for English language clients
        try:
            await bot.set_my_commands(
                [
                    BotCommand(command="start", description="Main menu & access check"),
                    BotCommand(command="quiz", description="Start quiz session"),
                    BotCommand(command="stop", description="Stop active quiz session"),
                    BotCommand(command="stats", description="View question statistics"),
                    BotCommand(command="help", description="Help & command guide"),
                    BotCommand(command="lang", description="Change interface language"),
                ],
                language_code="en",
            )
        except Exception:
            pass
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
