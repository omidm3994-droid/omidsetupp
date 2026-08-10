from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.jsondb import load_json, save_json
from utils.jalali import get_jalali_datetime

USERS_DB = "database/users.json"

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_json(USERS_DB)

    # اگر قبلاً ثبت‌نام کرده بود
    if user_id in users and users[user_id].get("registered", False):
        await update.message.reply_text("شما قبلاً ثبت‌نام کرده‌اید ✔️")
        return

    # پیام خوشامد + تاریخ شمسی
    jalali_time = get_jalali_datetime()
    await update.message.reply_text(
        f"سلام خوش اومدی 🌟\n\n"
        f"⏰ تاریخ و ساعت: {jalali_time}\n\n"
        "برای فعال شدن ربات، لطفاً اطلاعات زیر را مرحله‌به‌مرحله ارسال کن.\n\n"
        "اول: نام خودت را ارسال کن:"
    )

    context.user_data["reg_step"] = "name"


async def registration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    users = load_json(USERS_DB)

    step = context.user_data.get("reg_step")

    # مرحله ۱ — نام
    if step == "name":
        context.user_data["name"] = update.message.text
        context.user_data["reg_step"] = "lastname"
        await update.message.reply_text("عالیه ✔️ حالا نام خانوادگی را ارسال کن:")
        return

    # مرحله ۲ — نام خانوادگی
    if step == "lastname":
        context.user_data["lastname"] = update.message.text
        context.user_data["reg_step"] = "city"
        await update.message.reply_text("شهرت را ارسال کن:")
        return

    # مرحله ۳ — شهر
    if step == "city":
        context.user_data["city"] = update.message.text
        context.user_data["reg_step"] = "phone"
        await update.message.reply_text("شماره تماس را ارسال کن:")
        return

    # مرحله ۴ — شماره تماس
    if step == "phone":
        context.user_data["phone"] = update.message.text

        # ذخیره در دیتابیس
        users[user_id] = {
            "name": context.user_data["name"],
            "lastname": context.user_data["lastname"],
            "city": context.user_data["city"],
            "phone": context.user_data["phone"],
            "registered": True,
            "ai_usage": 0,
            "referrals": 0,
            "courses": {},
        }

        save_json(USERS_DB, users)

        # پیام فعال‌سازی
        await update.message.reply_text(
            "ثبت‌نام با موفقیت انجام شد 🎉\n"
            "ربات برای شما فعال شد ✔️"
        )

        # نمایش منوی اصلی
        from modules.menu import send_main_menu
        await send_main_menu(update, context)

        return
