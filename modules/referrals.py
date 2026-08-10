from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.jsondb import load_json, save_json

USERS_DB = "database/users.json"
SETTINGS_DB = "database/settings.json"

# دکمه ممبرگیری در منوی کاربر
async def referral_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.callback_query.from_user.id)
    users = load_json(USERS_DB)
    settings = load_json(SETTINGS_DB)

    # اگر سیستم فعال نیست
    if not settings["member_system"]["enabled"]:
        await update.callback_query.message.edit_text(
            "سیستم ممبرگیری فعال نیست ❌"
        )
        return

    # لینک دعوت اختصاصی
    invite_link = f"https://t.me/{context.bot.username}?start={user_id}"

    keyboard = [
        [InlineKeyboardButton("🔗 کپی لینک دعوت", url=invite_link)],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]

    await update.callback_query.message.edit_text(
        f"👥 سیستم ممبرگیری فعال است.\n"
        f"نوع ممبرگیری: {settings['member_system']['type']}\n\n"
        f"🔗 لینک دعوت اختصاصی شما:\n{invite_link}\n\n"
        f"👤 زیرمجموعه‌های شما: {users[user_id]['referrals']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ثبت زیرمجموعه هنگام ورود
async def check_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.startswith("/start"):
        parts = update.message.text.split()
        if len(parts) == 2:
            ref_id = parts[1]
            user_id = str(update.message.from_user.id)

            if ref_id != user_id:  # جلوگیری از دعوت خود
                users = load_json(USERS_DB)

                # اگر کاربر جدید است
                if user_id not in users:
                    users[user_id] = {
                        "name": "",
                        "lastname": "",
                        "city": "",
                        "phone": "",
                        "registered": False,
                        "ai_usage": 0,
                        "referrals": 0,
                        "courses": {}
                    }

                # افزایش زیرمجموعه
                if ref_id in users:
                    users[ref_id]["referrals"] += 1

                save_json(USERS_DB, users)
