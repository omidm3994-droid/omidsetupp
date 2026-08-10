from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.jsondb import load_json, save_json
from utils.gemini import ai_generate_text, ai_generate_image

USERS_DB = "database/users.json"
AI_DB = "database/ai_usage.json"

async def start_ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.callback_query.from_user.id)

    ai_data = load_json(AI_DB)
    users = load_json(USERS_DB)

    # اگر کاربر اولین بار استفاده می‌کند
    if user_id not in ai_data:
        ai_data[user_id] = {
            "usage": 0,
            "required_referrals": 0
        }
        save_json(AI_DB, ai_data)

    # بررسی محدودیت استفاده
    usage = ai_data[user_id]["usage"]
    required_refs = ai_data[user_id]["required_referrals"]
    user_refs = users[user_id]["referrals"]

    # اگر کاربر باید زیرمجموعه بیاورد
    if user_refs < required_refs:
        await update.callback_query.message.edit_text(
            f"⚠️ برای ادامه استفاده از هوش مصنوعی باید {required_refs} زیرمجموعه داشته باشید.\n"
            f"🔹 زیرمجموعه فعلی: {user_refs}"
        )
        return

    # نمایش صفحه چت
    keyboard = [
        [InlineKeyboardButton("✏️ تولید متن", callback_data="ai_text")],
        [InlineKeyboardButton("🖼 تولید تصویر", callback_data="ai_image")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]

    await update.callback_query.message.edit_text(
        "🤖 چت هوش مصنوعی فعال شد.\n"
        "یک گزینه را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ai_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "متن مورد نظر را ارسال کن:"
    )
    context.user_data["ai_mode"] = "text"


async def ai_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "توضیح تصویر مورد نظر را ارسال کن:"
    )
    context.user_data["ai_mode"] = "image"


async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    ai_data = load_json(AI_DB)
    users = load_json(USERS_DB)

    mode = context.user_data.get("ai_mode")
    prompt = update.message.text

    # افزایش تعداد استفاده
    ai_data[user_id]["usage"] += 1
    usage = ai_data[user_id]["usage"]

    # تعیین زیرمجموعه لازم
    if usage == 5:
        ai_data[user_id]["required_referrals"] = 2
    elif usage > 5 and (usage - 5) % 10 == 0:
        ai_data[user_id]["required_referrals"] += 3

    save_json(AI_DB, ai_data)

    # تولید متن
    if mode == "text":
        result = ai_generate_text(prompt)
        await update.message.reply_text(result)
        return

    # تولید تصویر
    if mode == "image":
        image = ai_generate_image(prompt)
        await update.message.reply_photo(image)
        return
