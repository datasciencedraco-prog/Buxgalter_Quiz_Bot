# Asynchronous Quiz Telegram Bot

A production-ready Telegram Quiz Bot built using **Python 3**, **`aiogram` (v3.x)**, and **`python-docx`**.
The bot ingests question sets directly from Word (`.docx`) files, implements interactive role-based access approval for test-takers, and delivers randomized quiz sessions via native Telegram Quiz Polls with unlimited retakes.

---

## 🌟 Key Features

1. **DOCX Ingestion Engine**:
   - Parses question blocks separated by `+++` and sections delimited by `===`.
   - Validates option counts (2 to 10 options, complying with Telegram poll limits).
   - Identifies the single correct answer marked with `#`, `+`, `✅`, or `✓` and cleanly strips markers.
   - Gracefully ignores malformed or incomplete question blocks.
   - Admin uploads `.docx` directly in Telegram chat to update or reload the question bank.

2. **Role-Based Access Control & Interactive Approvals**:
   - Only authorized users (saved in SQLite and synchronized to `allowed_users.json`) can take quizzes.
   - Unauthorized users see an inline `[📩 Request Access]` button on `/start`.
   - Clicking sends an instant approval request to `ADMIN_ID` with the user's Full Name, Username, and User ID.
   - Admin approves or rejects with inline buttons `[✅ Approve]` and `[❌ Reject]`.
   - Upon approval, the user receives an immediate notification and can take quizzes indefinitely.

3. **Randomized Quiz Sessions & Real-Time Scoring**:
   - Authorized users trigger tests via `/quiz`.
   - **Full randomization**: Question order is shuffled, and options within each question are dynamically shuffled on every attempt.
   - Sent sequentially as native Telegram Quiz Polls (`type="quiz"`, `is_anonymous=False`).
   - Real-time score calculation and automatic progression to the next question via `@router.poll_answer()`.
   - Summary upon completion showing total score, percentage, and prompt for unlimited retakes.

---

## 📁 Project Structure

```
├── .env.example          # Environment variable template
├── requirements.txt      # Project dependencies
├── config.py             # Pydantic Settings configuration loader
├── parser.py             # DOCX question template parsing logic
├── storage.py            # SQLite database & JSON synchronization manager
├── bot.py                # aiogram routers, handlers, and poll listeners
├── main.py               # Main bot entry point
├── test_parser.py        # Pytest unit tests for DOCX parsing (in-memory)
├── test_storage.py       # Pytest unit tests for storage and sessions
└── sample_quiz.docx      # Ready-to-use sample test file
```

---

## 📋 Word Document (.docx) Format Standard

Each question block must be structured as follows:

```text
+++
Question text goes here
===
First option
===
#Correct option (marked with #, +, ✅, or ✓)
===
Third option
===
Fourth option
+++
```

### Supported Correct Answer Markers:
- `#` (e.g., `#Tashkent`)
- `+` (e.g., `+ Tashkent`)
- `✅` (e.g., `✅ Tashkent`)
- `✓` (e.g., `✓ Tashkent`)

---

## 🚀 Setup & Installation

### 1. Create and Activate Virtual Environment
```bash
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```
Inside `.env`:
```env
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567
ADMIN_ID=123456789
```

### 4. Run Unit Tests
```bash
pytest -v
```

### 5. Launch the Bot
```bash
python main.py
```

---

## 🤖 Bot Commands

| Command | Tavsif (O'zbekcha) | Description (English) |
|---|---|---|
| `/start` | Asosiy menyu va ruxsatni tekshirish | Welcome screen & access verification |
| `/quiz` | Tasodifiy yangi testni boshlash | Start a new randomized quiz session |
| `/stop` | Joriy testni to'xtatish va natijani ko'rish | Stop the active quiz session and see current score |
| `/stats` | Savollar bazasi va holat statistikasi | View question bank count and authorization status |
| `/help` | Yo'riqnoma va yordam | Bot command guide and usage tips |
| `/lang` | Interfeys tilini tanlash (O'zbekcha / English) | Choose interface language |
| `/users` | *(Faqat admin)* Tasdiqlangan foydalanuvchilar ro'yxati | *(Admin only)* View approved users list & revoke buttons |
| `/revoke <id>` | *(Faqat admin)* Foydalanuvchi ruxsatini bekor qilish | *(Admin only)* Revoke user access by Telegram ID |
| *Send `.docx`* | *(Faqat admin)* Savollar bazasini yangilash | *(Admin only)* Upload a `.docx` file to reload questions |
