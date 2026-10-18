"""
Localization dictionary and text retrieval helpers for Uzbek and English.
"""

from typing import Any, Dict

MESSAGES: Dict[str, Dict[str, str]] = {
    "uz": {
        # Welcome & access
        "welcome_approved": (
            "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
            "Siz test topshirish uchun ruxsatga egasiz.\n\n"
            "📌 <b>Buyruqlar:</b>\n"
            "• /quiz - Testni boshlash (cheksiz urinishlar)\n"
            "• /stop - Testni to'xtatish\n"
            "• /stats - Savollar bazasi va statistika\n"
            "• /help - Yo'riqnoma va yordam\n"
            "• /lang - Tilni almashtirish"
        ),
        "admin_note": (
            "\n\n🛠 <b>Admin rejimi:</b> Savollar bazasini yangilash uchun "
            "to'g'ridan-to'g'ri <code>.docx</code> faylini yuborishingiz mumkin."
        ),
        "welcome_restricted": (
            "🔒 <b>Kirish cheklangan</b>\n\n"
            "Sizda hozircha test topshirish uchun ruxsat yo'q.\n"
            "Administratorga so'rov yuborish uchun quyidagi tugmani bosing."
        ),
        "btn_request_access": "📩 Ruxsat so'rash",
        "btn_approve": "✅ Tasdiqlash",
        "btn_reject": "❌ Rad etish",
        "already_approved": "Siz allaqachon tasdiqlangansiz!",
        "admin_request_title": (
            "🔔 <b>Yangi kirish so'rovi</b>\n\n"
            "👤 <b>F.I.O:</b> {full_name}\n"
            "🏷 <b>Username:</b> {username}\n"
            "🆔 <b>Foydalanuvchi ID:</b> <code>{user_id}</code>"
        ),
        "request_submitted": (
            "⏳ <b>So'rov yuborildi</b>\n\n"
            "Sizning so'rovingiz administratorga yuborildi. Ruxsat berilganda sizga xabar keladi."
        ),
        "request_sent_toast": "So'rov administratorga yuborildi.",
        "admin_error_toast": "Administrator bilan bog'lanib bo'lmadi. Keyinroq urinib ko'ring.",
        "access_denied_admin": "Ruxsat berilmadi. Faqat administrator uchun.",
        "admin_approved_label": "✅ <b>TASDIQLANDI</b>",
        "user_approved_notice": (
            "🎉 <b>Ruxsat berildi!</b>\n\n"
            "Administrator sizga test topshirish uchun ruxsat berdi. Endi istalgan vaqtda test topshirishingiz mumkin!\n\n"
            "👉 Boshlash uchun /quiz buyrug'ini bosing."
        ),
        "admin_rejected_label": "❌ <b>RAD ETILDI</b>",
        "user_rejected_notice": "❌ Sizning so'rovingiz administrator tomonidan rad etildi.",

        # Help & Stats
        "help_text": (
            "📖 <b>Buxgalteriya Test Boti bo'yicha yo'riqnoma</b>\n\n"
            "• /start - Ruxsatni tekshirish va asosiy menyu\n"
            "• /quiz - Tasodifiy test topshirishni boshlash\n"
            "• /stop - Joriy testni to'xtatish va natijani ko'rish\n"
            "• /stats - Savollar bazasi va holatni ko'rish\n"
            "• /lang - Interfeys tilini almashtirish\n\n"
            "<i>Har bir urinishda savollar va javob variantlari tasodifiy aralashtiriladi.</i>"
        ),
        "stats_text": (
            "📊 <b>Bot statistikasi</b>\n\n"
            "📚 Bazadagi savollar soni: <b>{count} ta</b>\n"
            "👤 Sizning holatingiz: <b>{status}</b>\n"
            "🌐 Interfeys tili: <b>{lang_name}</b>"
        ),
        "status_approved": "Tasdiqlangan",
        "status_pending": "Kutilmoqda",

        # Quiz & Session
        "quiz_denied": "🔒 <b>Kirish taqiqlangan</b>\n\nTest topshirish uchun sizda ruxsat yo'q. Ruxsat olish uchun /start buyrug'ini yuboring.",
        "bank_empty": "⚠️ <b>Savollar bazasi bo'sh.</b>\nIltimos, administrator test savollarini yuklashini kuting.",
        "quiz_started": (
            "🎯 <b>Test boshlandi!</b>\n"
            "Jami savollar soni: <b>{total} ta</b>\n\n"
            "<i>Barcha savollar va javob variantlari tasodifiy aralashtirildi. Omad!</i>\n"
            "<i>Testni istalgan vaqtda to'xtatish uchun /stop buyrug'ini yuboring.</i>"
        ),
        "quiz_completed": (
            "🏁 <b>Test yakunlandi!</b>\n\n"
            "📊 <b>Sizning natijangiz:</b> <b>{score} / {total}</b> ({pct:.1f}%)\n\n"
            "🔄 <i>Testni qayta topshirish uchun /quiz buyrug'ini bosing!</i>"
        ),
        "stop_no_session": "ℹ️ <b>Faol test topilmadi.</b>\n\nYangi testni boshlash uchun /quiz buyrug'ini yuboring.",
        "stop_with_score": (
            "🛑 <b>Test to'xtatildi</b>\n\n"
            "📊 <b>Bajarilgan savollar:</b> {answered} / {total} ta\n"
            "⭐ <b>To'plangan ball:</b> <b>{score} / {answered}</b> ({pct:.1f}%)\n\n"
            "🔄 <i>Yangi test boshlash uchun istalgan vaqtda /quiz buyrug'ini bosing!</i>"
        ),
        "stop_cancelled": (
            "🛑 <b>Test to'xtatildi</b>\n\n"
            "Test bekor qilindi.\n\n"
            "🔄 <i>Boshlashga tayyor bo'lganingizda /quiz buyrug'ini bosing!</i>"
        ),

        # Document upload
        "doc_admin_only": "⚠️ Faqat administrator test fayllarini yuklashi mumkin.",
        "doc_invalid_ext": "⚠️ Iltimos, faqat <code>.docx</code> formatidagi Word hujjatini yuboring.",
        "doc_ingesting": "⏳ <code>{filename}</code> yuklanmoqda va tekshirilmoqda...",
        "doc_no_questions": (
            "❌ <b>{filename}</b> faylida yaroqli savollar topilmadi.\n\n"
            "Iltimos, shablon formatini tekshiring:\n"
            "• Savol bloklari orasida <code>+++</code>\n"
            "• Savol matni va variantlar orasida <code>===</code>\n"
            "• To'g'ri javob oldida <code>#</code>, <code>+</code>, <code>✅</code> yoki <code>✓</code>"
        ),
        "doc_success": (
            "✅ <b>Savollar bazasi yangilandi!</b>\n\n"
            "📄 <b>Fayl:</b> <code>{filename}</code>\n"
            "📥 <b>Qo'shilgan savollar:</b> {parsed} ta\n"
            "📚 <b>Bazadagi jami savollar:</b> {total} ta\n\n"
            "Tasdiqlangan foydalanuvchilar endi /quiz orqali test topshirishlari mumkin."
        ),

        # User management (Admin)
        "users_title": "👥 <b>Tasdiqlangan foydalanuvchilar</b> (Jami: {total} ta):\n",
        "no_other_users": "ℹ️ Hozircha tasdiqlangan boshqa foydalanuvchilar mavjud emas.\n(Faqat administrator ro'yxatda).",
        "btn_revoke_user": "❌ O'chirish: {name} ({uid})",
        "user_revoked_success": "✅ Foydalanuvchi (ID: <code>{uid}</code>) ruxsati bekor qilindi.",
        "user_not_found": "⚠️ Bunday ID ga ega tasdiqlangan foydalanuvchi topilmadi.",
        "cannot_revoke_admin": "⚠️ Administrator hisobini o'chirib bo'lmaydi.",
        "user_revoked_alert": "⚠️ Administrator tomonidan test topshirish ruxsatingiz bekor qilindi.",
        "kb_users": "👥 Foydalanuvchilar",
        "revoke_usage": "\n💡 <i>Ruxsatni bekor qilish uchun yuqoridagi tugmani bosing yoki <code>/revoke [ID]</code> buyrug'ini yuboring.</i>",

        # Keyboard & language
        "choose_lang": "🌐 <b>Iltimos, tilni tanlang / Please choose a language:</b>",
        "lang_changed": "✅ Interfeys tili <b>O'zbekcha</b>ga o'zgartirildi.",
        "kb_quiz": "🎯 Testni boshlash",
        "kb_stop": "🛑 To'xtatish",
        "kb_stats": "📊 Statistika",
        "kb_help": "📖 Yo'riqnoma",
        "kb_lang": "🌐 Tilni almashtirish",
    },
    "en": {
        # Welcome & access
        "welcome_approved": (
            "👋 Welcome, <b>{name}</b>!\n\n"
            "You are authorized to take quizzes.\n\n"
            "📌 <b>Commands:</b>\n"
            "• /quiz - Start a new quiz session (unlimited retakes)\n"
            "• /stop - Stop current quiz session\n"
            "• /stats - View question bank and session status\n"
            "• /help - View instructions\n"
            "• /lang - Change interface language"
        ),
        "admin_note": (
            "\n\n🛠 <b>Admin Mode:</b> You can upload <code>.docx</code> test "
            "files directly to update the question bank."
        ),
        "welcome_restricted": (
            "🔒 <b>Access Restricted</b>\n\n"
            "You are not currently authorized to take tests.\n"
            "Click the button below to request access from the administrator."
        ),
        "btn_request_access": "📩 Request Access",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "already_approved": "You are already approved!",
        "admin_request_title": (
            "🔔 <b>New Access Request</b>\n\n"
            "👤 <b>Full Name:</b> {full_name}\n"
            "🏷 <b>Username:</b> {username}\n"
            "🆔 <b>User ID:</b> <code>{user_id}</code>"
        ),
        "request_submitted": (
            "⏳ <b>Access Request Submitted</b>\n\n"
            "Your request has been forwarded to the administrator. You will be notified when approved."
        ),
        "request_sent_toast": "Request sent to administrator.",
        "admin_error_toast": "Unable to contact administrator. Please try again later.",
        "access_denied_admin": "Access denied. Admin only.",
        "admin_approved_label": "✅ <b>APPROVED</b>",
        "user_approved_notice": (
            "🎉 <b>Access Approved!</b>\n\n"
            "The administrator has approved your access. You can now start the quiz at any time!\n\n"
            "👉 Type /quiz to begin."
        ),
        "admin_rejected_label": "❌ <b>REJECTED</b>",
        "user_rejected_notice": "❌ Your access request was not approved by the administrator.",

        # Help & Stats
        "help_text": (
            "📖 <b>Quiz Bot Help</b>\n\n"
            "• /start - Verify authorization and show main menu\n"
            "• /quiz - Begin a randomized quiz session\n"
            "• /stop - Stop current quiz session early\n"
            "• /stats - View question bank and session status\n"
            "• /lang - Change interface language\n\n"
            "<i>Questions and options are randomly shuffled on every attempt.</i>"
        ),
        "stats_text": (
            "📊 <b>Bot Statistics</b>\n\n"
            "📚 Available Questions: <b>{count}</b>\n"
            "👤 Your Status: <b>{status}</b>\n"
            "🌐 Current Language: <b>{lang_name}</b>"
        ),
        "status_approved": "Approved",
        "status_pending": "Pending Approval",

        # Quiz & Session
        "quiz_denied": "🔒 <b>Access Denied</b>\n\nYou must be approved to take the quiz. Use /start to request access.",
        "bank_empty": "⚠️ <b>Question bank is empty.</b>\nPlease wait for the administrator to upload test questions.",
        "quiz_started": (
            "🎯 <b>Quiz Session Started!</b>\n"
            "Total Questions: <b>{total}</b>\n\n"
            "<i>All questions and answer options are randomly shuffled. Good luck!</i>\n"
            "<i>Type /stop at any time to end the quiz early.</i>"
        ),
        "quiz_completed": (
            "🏁 <b>Quiz Completed!</b>\n\n"
            "📊 <b>Your Score:</b> <b>{score} / {total}</b> ({pct:.1f}%)\n\n"
            "🔄 <i>You can retake the quiz anytime by typing /quiz!</i>"
        ),
        "stop_no_session": "ℹ️ <b>No active quiz session found.</b>\n\nType /quiz to start a new quiz.",
        "stop_with_score": (
            "🛑 <b>Quiz Stopped</b>\n\n"
            "📊 <b>Progress:</b> {answered} of {total} questions\n"
            "⭐ <b>Score so far:</b> <b>{score} / {answered}</b> ({pct:.1f}%)\n\n"
            "🔄 <i>Type /quiz whenever you'd like to start a new quiz!</i>"
        ),
        "stop_cancelled": (
            "🛑 <b>Quiz Stopped</b>\n\n"
            "Your quiz session has been cancelled.\n\n"
            "🔄 <i>Type /quiz whenever you'd like to begin!</i>"
        ),

        # Document upload
        "doc_admin_only": "⚠️ Only the administrator can upload test documents.",
        "doc_invalid_ext": "⚠️ Please send a valid Word document ending with <code>.docx</code>.",
        "doc_ingesting": "⏳ Ingesting <code>{filename}</code>...",
        "doc_no_questions": (
            "❌ <b>No valid questions found</b> in <code>{filename}</code>.\n\n"
            "Please verify the template format:\n"
            "• <code>+++</code> separates question blocks\n"
            "• <code>===</code> separates question text and options\n"
            "• One correct answer marked with <code>#</code>, <code>+</code>, <code>✅</code>, or <code>✓</code>"
        ),
        "doc_success": (
            "✅ <b>Ingestion Complete!</b>\n\n"
            "📄 <b>File:</b> <code>{filename}</code>\n"
            "📥 <b>Parsed Questions:</b> {parsed}\n"
            "📚 <b>Total Questions in Database:</b> {total}\n\n"
            "Approved users can now take the test with /quiz."
        ),

        # User management (Admin)
        "users_title": "👥 <b>Approved Users</b> (Total: {total}):\n",
        "no_other_users": "ℹ️ No other approved users found.\n(Only administrator is registered).",
        "btn_revoke_user": "❌ Remove: {name} ({uid})",
        "user_revoked_success": "✅ Access for user (ID: <code>{uid}</code>) was successfully revoked.",
        "user_not_found": "⚠️ No approved user found with this ID.",
        "cannot_revoke_admin": "⚠️ Cannot revoke administrator access.",
        "user_revoked_alert": "⚠️ Your access to take quizzes has been revoked by the administrator.",
        "kb_users": "👥 Users",
        "revoke_usage": "\n💡 <i>To revoke access, click a button above or type <code>/revoke [ID]</code>.</i>",

        # Keyboard & language
        "choose_lang": "🌐 <b>Please choose a language / Tilni tanlang:</b>",
        "lang_changed": "✅ Language changed to <b>English</b>.",
        "kb_quiz": "🎯 Start Quiz",
        "kb_stop": "🛑 Stop Quiz",
        "kb_stats": "📊 Statistics",
        "kb_help": "📖 Help",
        "kb_lang": "🌐 Change Language",
    },
}

LANGUAGE_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
}


def get_text(key: str, lang: str = "uz", **kwargs: Any) -> str:
    """Retrieve localized message string with fallback to Uzbek."""
    lang_dict = MESSAGES.get(lang, MESSAGES["uz"])
    template = lang_dict.get(key, MESSAGES["uz"].get(key, key))
    if kwargs:
        return template.format(**kwargs)
    return template


def get_lang_display(lang: str = "uz") -> str:
    return LANGUAGE_NAMES.get(lang, "🇺🇿 O'zbekcha")
