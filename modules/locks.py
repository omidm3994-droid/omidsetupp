from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.jsondb import load_json, save_json

USERS_DB = "database/users.json"
COURSES_DB = "database/courses.json"
PAYMENTS_DB = "database/payments.json"

# شروع قفل‌گذاری توسط ادمین
async def lock_course_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    courses = load_json(COURSES_DB)

    keyboard = []
    for cid, info in courses.items():
        keyboard.append([
            InlineKeyboardButton(info["title"], callback_data=f"lock_select_{cid}")
        ])

    await update.callback_query.message.edit_text(
        "🔒 انتخاب دوره برای قفل‌گذاری:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# انتخاب نوع قفل
async def lock_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.callback_query.data.replace("lock_select_", "")
    context.user_data["lock_course"] = cid

    keyboard = [
        [InlineKeyboardButton("👥 قفل زیرمجموعه", callback_data="lock_referral")],
        [InlineKeyboardButton("💳 قفل پرداخت", callback_data="lock_payment")],
        [InlineKeyboardButton("❌ لغو", callback_data="admin_panel")]
    ]

    await update.callback_query.message.edit_text(
        "نوع قفل را انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# قفل زیرمجموعه
async def lock_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "تعداد زیرمجموعه لازم را ارسال کن:"
    )
    context.user_data["lock_mode"] = "referral"


# قفل پرداخت
async def lock_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "مبلغ دوره را ارسال کن:"
    )
    context.user_data["lock_mode"] = "payment"


# دریافت مقدار قفل
async def lock_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("lock_mode")
    cid = context.user_data.get("lock_course")

    courses = load_json(COURSES_DB)

    if mode == "referral":
        value = int(update.message.text)
        courses[cid]["locked"] = True
        courses[cid]["lock_type"] = "referral"
        courses[cid]["required_referrals"] = value
        save_json(COURSES_DB, courses)

        await update.message.reply_text(
            f"قفل زیرمجموعه فعال شد ✔️\n"
            f"تعداد لازم: {value}"
        )
        return

    if mode == "payment":
        value = int(update.message.text)
        courses[cid]["locked"] = True
        courses[cid]["lock_type"] = "payment"
        courses[cid]["price"] = value
        save_json(COURSES_DB, courses)

        await update.message.reply_text(
            f"قفل پرداخت فعال شد ✔️\n"
            f"مبلغ لازم: {value} تومان"
        )
        return


# بررسی قفل هنگام انتخاب دوره
async def check_course_lock(update: Update, context: ContextTypes.DEFAULT_TYPE, cid):
    query = update.callback_query
    user_id = str(query.from_user.id)

    users = load_json(USERS_DB)
    courses = load_json(COURSES_DB)

    course = courses[cid]

    # اگر قفل نبود → آزاد
    if not course["locked"]:
        return "open"

    # قفل زیرمجموعه
    if course["lock_type"] == "referral":
        required = course["required_referrals"]
        current = users[user_id]["referrals"]

        if current < required:
            await query.message.edit_text(
                f"🔒 این دوره قفل است.\n"
                f"برای باز شدن باید {required} زیرمجموعه داشته باشید.\n"
                f"زیرمجموعه فعلی: {current}"
            )
            return "locked"

        return "open"

    # قفل پرداخت
    if course["lock_type"] == "payment":
        price = course["price"]

        keyboard = [
            [InlineKeyboardButton("📤 ارسال فیش", callback_data=f"send_fish_{cid}")],
            [InlineKeyboardButton("🔙 برگشت", callback_data="edu")]
        ]

        await query.message.edit_text(
            f"🔒 این دوره قفل است.\n"
            f"برای باز شدن باید مبلغ {price} تومان پرداخت کنید.\n"
      f"پس از پرداخت، فیش را ارسال کنید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return "locked"

    return "locked"


# دریافت فیش
async def receive_fish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    cid = context.user_data.get("fish_course")

    payments = load_json(PAYMENTS_DB)

    payments[user_id] = {
        "course": cid,
        "file_id": update.message.photo[-1].file_id,
        "status": "pending"
    }

    save_json(PAYMENTS_DB, payments)

    # ارسال به ادمین اصلی
    admin_id = load_json("database/admins.json")["main_admin"]

    keyboard = [
        [InlineKeyboardButton("✔️ تأیید", callback_data=f"fish_ok_{user_id}")],
        [InlineKeyboardButton("❌ لغو", callback_data=f"fish_no_{user_id}")]
    ]

    await context.bot.send_photo(
        chat_id=admin_id,
        photo=update.message.photo[-1].file_id,
        caption=f"فیش جدید از کاربر {user_id}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text("فیش شما ارسال شد و در انتظار بررسی است ✔️")


# تأیید فیش
async def fish_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data.replace("fish_ok_", "")
    payments = load_json(PAYMENTS_DB)
    users = load_json(USERS_DB)

    cid = payments[user_id]["course"]
    payments[user_id]["status"] = "approved"

    # فعال‌سازی دوره
    users[user_id]["courses"][cid] = True

    save_json(PAYMENTS_DB, payments)
    save_json(USERS_DB, users)

    await update.callback_query.message.edit_text("فیش تأیید شد ✔️")
    await context.bot.send_message(
        chat_id=user_id,
        text="پرداخت شما تأیید شد ✔️\nدوره برای شما فعال شد.\nسپاس از اعتماد شما 🌟"
    )


# لغو فیش
async def fish_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data.replace("fish_no_", "")
    payments = load_json(PAYMENTS_DB)

    payments[user_id]["status"] = "rejected"
    save_json(PAYMENTS_DB, payments)

    await update.callback_query.message.edit_text("فیش لغو شد ❌")
    await context.bot.send_message(
        chat_id=user_id,
        text="پرداخت شما تأیید نشد.\nلطفاً با پشتیبانی تماس بگیرید."
    )
