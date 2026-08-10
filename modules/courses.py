from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.jsondb import load_json
from utils.jsondb import save_json

USERS_DB = "database/users.json"
COURSES_DB = "database/courses.json"

# اگر courses.json خالی باشد، دوره‌های پیشفرض را می‌سازیم
DEFAULT_COURSES = {
    "course_jame_bargh": {
        "title": "دوره جامع برق خودرو",
        "locked": False,
        "lock_type": None,   # referral / payment / None
        "required_referrals": 0,
        "price": 0
    },
    "course_takhasosi_bargh": {
        "title": "دوره تخصصی برق خودرو",
        "locked": False,
        "lock_type": None,
        "required_referrals": 0,
        "price": 0
    },
    "course_vip": {
        "title": "دوره VIP چندمنظوره",
        "locked": False,
        "lock_type": None,
        "required_referrals": 0,
        "price": 0
    },
    "course_jame_mek": {
        "title": "دوره جامع مکانیکی",
        "locked": False,
        "lock_type": None,
        "required_referrals": 0,
        "price": 0
    },
    "ai_chat": {
        "title": "هوش مصنوعی",
        "locked": False,
        "lock_type": None,
        "required_referrals": 0,
        "price": 0
    }
}

def load_courses():
    try:
        data = load_json(COURSES_DB)
        if not data:
            save_json(COURSES_DB, DEFAULT_COURSES)
            return DEFAULT_COURSES
        return data
    except:
        save_json(COURSES_DB, DEFAULT_COURSES)
        return DEFAULT_COURSES


async def open_courses_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    courses = load_courses()

    keyboard = []
    for cid, info in courses.items():
        keyboard.append([
            InlineKeyboardButton(info["title"], callback_data=f"course_{cid}")
        ])

    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_main")])

    await update.callback_query.message.edit_text(
        "📚 دوره‌های آموزشی:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def course_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.replace("course_", "")

    courses = load_courses()
    users = load_json(USERS_DB)
    user_id = str(query.from_user.id)

    course = courses.get(data)

    # اگر دوره قفل باشد → در مرحله بعدی سیستم قفل را کامل می‌سازیم
    if course["locked"]:
        await query.message.edit_text(
            "این دوره قفل است 🔒\n"
            "در مرحله بعدی سیستم قفل را فعال می‌کنیم."
        )
        return

    # اگر دوره هوش مصنوعی باشد → چت جداگانه
    if data == "ai_chat":
        from modules.ai_chat import start_ai_chat
        await start_ai_chat(update, context)
        return

    # نمایش اطلاعات دوره
    await query.message.edit_text(
        f"📘 {course['title']}\n\n"
        "در مرحله بعدی:\n"
        "• فایل PDF اضافه می‌کنیم\n"
        "• قفل زیرمجموعه / پرداخت فعال می‌کنیم\n"
        "• مدیریت دوره‌ها را در پنل ادمین می‌سازیم\n\n"
        "فعلاً این بخش فقط نمایش اولیه است."
    )
