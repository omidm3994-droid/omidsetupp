from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.jsondb import load_json, save_json
from utils.jalali import get_jalali_datetime
from utils.gemini import ai_generate_text

USERS_DB = "database/users.json"
ADMINS_DB = "database/admins.json"
SETTINGS_DB = "database/settings.json"
TEXTS_DB = "database/texts.json"
BUTTONS_DB = "database/buttons.json"
COURSES_DB = "database/courses.json"


# ---------------------------------------------------------
# 1) پنل مدیریت اصلی
# ---------------------------------------------------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.callback_query.from_user.id)
    admins = load_json(ADMINS_DB)

    if user_id not in admins["admins"] and user_id != admins["main_admin"]:
        await update.callback_query.message.edit_text("❌ شما ادمین نیستید.")
        return

    keyboard = [
        [InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats")],
        [InlineKeyboardButton("👤 مدیریت ادمین‌ها", callback_data="admin_manage_admins")],
        [InlineKeyboardButton("📢 عضویت اجباری", callback_data="admin_force_join")],
        [InlineKeyboardButton("👥 ممبرگیری حرفه‌ای", callback_data="member_system")],
        [InlineKeyboardButton("📝 مدیریت متن‌ها", callback_data="admin_texts")],
        [InlineKeyboardButton("🔘 مدیریت دکمه‌ها", callback_data="admin_buttons")],
        [InlineKeyboardButton("📚 مدیریت دوره‌ها", callback_data="admin_courses")],
        [InlineKeyboardButton("🔒 قفل دوره‌ها", callback_data="lock_course")],
        [InlineKeyboardButton("📨 ارسال همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📨 فوروارد همگانی", callback_data="admin_forward")],
        [InlineKeyboardButton("⏱ پیام خودکار", callback_data="admin_auto_msg")],
        [InlineKeyboardButton("📂 خروجی کاربران", callback_data="admin_export")],
        [InlineKeyboardButton("🤖 دستیار مدیران", callback_data="admin_ai")],
        [InlineKeyboardButton("📘 راهنمای مدیران", callback_data="admin_help")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]

    await update.callback_query.message.edit_text(
        "🔧 پنل مدیریت ربات",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------------------------------------------------
# 2) آمار ربات
# ---------------------------------------------------------
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_DB)
    admins = load_json(ADMINS_DB)

    total_users = len(users)
    total_admins = len(admins["admins"])
    jalali_time = get_jalali_datetime()

    await update.callback_query.message.edit_text(
        f"📊 آمار ربات:\n\n"
        f"👤 کاربران: {total_users}\n"
        f"🛡 ادمین‌ها: {total_admins}\n"
        f"⏰ تاریخ شمسی: {jalali_time}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
        ])
    )


# ---------------------------------------------------------
# 3) مدیریت ادمین‌ها
# ---------------------------------------------------------
async def admin_manage_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_json(ADMINS_DB)

    keyboard = [
        [InlineKeyboardButton("➕ افزودن ادمین", callback_data="admin_add")],
        [InlineKeyboardButton("➖ حذف ادمین", callback_data="admin_remove")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
    ]

    await update.callback_query.message.edit_text(
        f"👤 مدیریت ادمین‌ها\n\n"
        f"ادمین اصلی: {admins['main_admin']}\n"
        f"سایر ادمین‌ها: {admins['admins']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_json(ADMINS_DB)
    user_id = str(update.callback_query.from_user.id)

    if user_id != admins["main_admin"]:
        await update.callback_query.message.
      edit_text("❌ فقط ادمین اصلی می‌تواند ادمین اضافه کند.")
        return

    await update.callback_query.message.edit_text("شناسه کاربری فرد مورد نظر را ارسال کن:")
    context.user_data["admin_add_mode"] = True


async def admin_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("admin_add_mode"):
        new_admin = update.message.text
        admins = load_json(ADMINS_DB)

        admins["admins"].append(new_admin)
        save_json(ADMINS_DB, admins)

        await update.message.reply_text("✔️ ادمین جدید اضافه شد.")
        context.user_data["admin_add_mode"] = False


async def admin_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_json(ADMINS_DB)
    user_id = str(update.callback_query.from_user.id)

    if user_id != admins["main_admin"]:
        await update.callback_query.message.edit_text("❌ فقط ادمین اصلی می‌تواند ادمین حذف کند.")
        return

    await update.callback_query.message.edit_text("شناسه کاربری ادمین مورد نظر را ارسال کن:")
    context.user_data["admin_remove_mode"] = True


async def admin_remove_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("admin_remove_mode"):
        remove_admin = update.message.text
        admins = load_json(ADMINS_DB)

        if remove_admin in admins["admins"]:
            admins["admins"].remove(remove_admin)
            save_json(ADMINS_DB, admins)
            await update.message.reply_text("✔️ ادمین حذف شد.")
        else:
            await update.message.reply_text("❌ این شناسه ادمین نیست.")

        context.user_data["admin_remove_mode"] = False


# ---------------------------------------------------------
# 4) عضویت اجباری
# ---------------------------------------------------------
async def admin_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_json(SETTINGS_DB)

    keyboard = [
        [InlineKeyboardButton("🔛 فعال‌سازی", callback_data="force_on")],
        [InlineKeyboardButton("🔴 غیرفعال‌سازی", callback_data="force_off")],
        [InlineKeyboardButton("📢 تعیین کانال", callback_data="force_set_channel")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
    ]

    await update.callback_query.message.edit_text(
        f"📢 عضویت اجباری\n\n"
        f"وضعیت فعلی: {'فعال' if settings['force_join']['enabled'] else 'غیرفعال'}\n"
        f"کانال فعلی: {settings['force_join']['channel']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def force_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_json(SETTINGS_DB)
    settings["force_join"]["enabled"] = True
    save_json(SETTINGS_DB, settings)
    await update.callback_query.message.edit_text("✔️ عضویت اجباری فعال شد.")


async def force_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = load_json(SETTINGS_DB)
    settings["force_join"]["enabled"] = False
    save_json(SETTINGS_DB, settings)
    await update.callback_query.message.edit_text("❌ عضویت اجباری غیرفعال شد.")


async def force_set_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("لینک یا یوزرنیم کانال را ارسال کن:")
    context.user_data["force_channel_mode"] = True


async def force_set_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("force_channel_mode"):
        channel = update.message.text
        settings = load_json(SETTINGS_DB)

        settings["force_join"]["channel"] = channel
        save_json(SETTINGS_DB, settings)

        await update.message.reply_text("✔️ کانال عضویت اجباری تنظیم شد.")
        context.user_data["force_channel_mode"] = False


# ---------------------------------------------------------
# 5) مدیریت متن‌ها
# ---------------------------------------------------------
async def admin_texts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texts = load_json(TEXTS_DB)

    keyboard = []
    for key in texts.keys():
        keyboard.
      append([InlineKeyboardButton(key, callback_data=f"text_edit_{key}")])

    keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")])

    await update.callback_query.message.edit_text(
        "📝 انتخاب متن برای ویرایش:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def text_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.callback_query.data.replace("text_edit_", "")
    context.user_data["edit_text_key"] = key

    await update.callback_query.message.edit_text(
        f"متن جدید برای «{key}» را ارسال کن:"
    )


async def text_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data.get("edit_text_key")
    if not key:
        return

    texts = load_json(TEXTS_DB)
    texts[key] = update.message.text
    save_json(TEXTS_DB, texts)

    await update.message.reply_text("✔️ متن با موفقیت تغییر کرد.")
    context.user_data["edit_text_key"] = None


# ---------------------------------------------------------
# 6) مدیریت دکمه‌ها
# ---------------------------------------------------------
async def admin_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ افزودن دکمه", callback_data="btn_add")],
        [InlineKeyboardButton("➖ حذف دکمه", callback_data="btn_remove")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
    ]

    await update.callback_query.message.edit_text(
        "🔘 مدیریت دکمه‌ها",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def btn_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "نام بخش دکمه را ارسال کن:\n(main_menu / edu_menu / custom_buttons)"
    )
    context.user_data["btn_add_step"] = "section"


async def btn_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("btn_add_step")

    if step == "section":
        context.user_data["btn_section"] = update.message.text
        context.user_data["btn_add_step"] = "text"
        await update.message.reply_text("متن دکمه را ارسال کن:")
        return

    if step == "text":
        context.user_data["btn_text"] = update.message.text
        context.user_data["btn_add_step"] = "callback"
        await update.message.reply_text("callback دکمه را ارسال کن:")
        return

    if step == "callback":
        section = context.user_data["btn_section"]
        text = context.user_data["btn_text"]
        callback = update.message.text

        buttons = load_json(BUTTONS_DB)
        buttons[section].append({"text": text, "callback": callback})
        save_json(BUTTONS_DB, buttons)

        await update.message.reply_text("✔️ دکمه اضافه شد.")
        context.user_data["btn_add_step"] = None


async def btn_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "نام بخش دکمه را ارسال کن:\n(main_menu / edu_menu / custom_buttons)"
    )
    context.user_data["btn_remove_step"] = "section"


async def btn_remove_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("btn_remove_step")

    if step == "section":
        context.user_data["btn_section"] = update.message.text
        context.user_data["btn_remove_step"] = "callback"
        await update.message.reply_text("callback دکمه مورد نظر را ارسال کن:")
        return

    if step == "callback":
        section = context.user_data["btn_section"]
        callback = update.message.text

        buttons = load_json(BUTTONS_DB)
        buttons[section] = [b for b in buttons[section] if b["callback"] != callback]
        save_json(BUTTONS_DB, buttons)

        await update.message.reply_text("✔️ دکمه حذف شد.")
        context.user_data["btn_remove_step"] = None


# ---------------------------------------------------------
# 7) مدیریت دوره‌ها
# ---------------------------------------------------------
async def admin_courses(update: Update, context: ContextTypes.DEFAULT_TYPE):
  courses = load_json(COURSES_DB)

    keyboard = [
        [InlineKeyboardButton("➕ افزودن دوره", callback_data="course_add")],
        [InlineKeyboardButton("➖ حذف دوره", callback_data="course_remove")],
        [InlineKeyboardButton("✏️ تغییر عنوان دوره", callback_data="course_edit_title")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
    ]

    await update.callback_query.message.edit_text(
        f"📚 مدیریت دوره‌ها\n\n"
        f"دوره‌های فعلی:\n{list(courses.keys())}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def course_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("شناسه دوره جدید را ارسال کن:")
    context.user_data["course_add_step"] = "id"


async def course_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("course_add_step")

    if step == "id":
        context.user_data["course_id"] = update.message.text
        context.user_data["course_add_step"] = "title"
        await update.message.reply_text("عنوان دوره را ارسال کن:")
        return

    if step == "title":
        cid = context.user_data["course_id"]
        title = update.message.text

        courses = load_json(COURSES_DB)
        courses[cid] = {
            "title": title,
            "locked": False,
            "lock_type": None,
            "required_referrals": 0,
            "price": 0
        }
        save_json(COURSES_DB, courses)

        await update.message.reply_text("✔️ دوره جدید اضافه شد.")
        context.user_data["course_add_step"] = None


async def course_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("شناسه دوره مورد نظر را ارسال کن:")
    context.user_data["course_remove_mode"] = True


async def course_remove_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("course_remove_mode"):
        cid = update.message.text
        courses = load_json(COURSES_DB)

        if cid in courses:
            del courses[cid]
            save_json(COURSES_DB, courses)
            await update.message.reply_text("✔️ دوره حذف شد.")
        else:
            await update.message.reply_text("❌ دوره یافت نشد.")

        context.user_data["course_remove_mode"] = False


async def course_edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("شناسه دوره را ارسال کن:")
    context.user_data["course_edit_step"] = "id"


async def course_edit_title_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("course_edit_step")

    if step == "id":
        context.user_data["course_id"] = update.message.text
        context.user_data["course_edit_step"] = "title"
        await update.message.reply_text("عنوان جدید دوره را ارسال کن:")
        return

    if step == "title":
        cid = context.user_data["course_id"]
        new_title = update.message.text

        courses = load_json(COURSES_DB)
        if cid in courses:
            courses[cid]["title"] = new_title
            save_json(COURSES_DB, courses)
            await update.message.reply_text("✔️ عنوان دوره تغییر کرد.")
        else:
            await update.message.reply_text("❌ دوره یافت نشد.")

        context.user_data["course_edit_step"] = None


# ---------------------------------------------------------
# 8) ارسال همگانی
# ---------------------------------------------------------
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("متن پیام همگانی را ارسال کن:")
    context.user_data["broadcast_mode"] = True


async def admin_broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("broadcast_mode"):
        text = update.message.text
        users = load_json(USERS_DB)

        for uid in users.keys():
            try:
                await context.bot.send_message(chat_id=uid, text=text)
            except:
              pass

        await update.message.reply_text("✔️ پیام همگانی ارسال شد.")
        context.user_data["broadcast_mode"] = False


# ---------------------------------------------------------
# 9) فوروارد همگانی
# ---------------------------------------------------------
async def admin_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("پیامی که می‌خواهی فوروارد شود را ارسال کن:")
    context.user_data["forward_mode"] = True


async def admin_forward_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("forward_mode"):
        users = load_json(USERS_DB)

        for uid in users.keys():
            try:
                await update.message.forward(chat_id=uid)
            except:
                pass

        await update.message.reply_text("✔️ فوروارد همگانی انجام شد.")
        context.user_data["forward_mode"] = False


# ---------------------------------------------------------
# 10) پیام خودکار
# ---------------------------------------------------------
async def admin_auto_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text("متن پیام خودکار را ارسال کن:")
    context.user_data["auto_msg_step"] = "text"


async def admin_auto_msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("auto_msg_step")

    if step == "text":
        context.user_data["auto_msg_text"] = update.message.text
        context.user_data["auto_msg_step"] = "time"
        await update.message.reply_text("زمان ارسال (به دقیقه) را ارسال کن:")
        return

        if step == "time":
        minutes = int(update.message.text)
        text = context.user_data["auto_msg_text"]

        settings = load_json(SETTINGS_DB)
        settings["auto_message"] = {
            "text": text,
            "minutes": minutes
        }
        save_json(SETTINGS_DB, settings)

        await update.message.reply_text("✔️ پیام خودکار تنظیم شد.")
        context.user_data["auto_msg_step"] = None


# ---------------------------------------------------------
# 11) خروجی کاربران بر اساس شهر
# ---------------------------------------------------------
async def admin_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_DB)

    cities = {}
    for uid, info in users.items():
        city = info["city"]
        if city not in cities:
            cities[city] = []
        cities[city].append(uid)

    text = "📂 خروجی کاربران بر اساس شهر:\n\n"
    for city, ids in cities.items():
        text += f"🏙 {city}: {len(ids)} نفر\n"

    await update.callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
        ])
    )


# ---------------------------------------------------------
# 12) دستیار هوش مصنوعی مدیران
# ---------------------------------------------------------
async def admin_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "متن مورد نظر برای تحلیل هوش مصنوعی را ارسال کن:"
    )
    context.user_data["admin_ai_mode"] = True


async def admin_ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("admin_ai_mode"):
        prompt = update.message.text
        result = ai_generate_text(prompt)

        await update.message.reply_text(result)
        context.user_data["admin_ai_mode"] = False


# ---------------------------------------------------------
# 13) راهنمای مدیران
# ---------------------------------------------------------
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.edit_text(
        "📘 راهنمای مدیران:\n\n"
        "• آمار ربات: نمایش تعداد کاربران\n"
        "• مدیریت ادمین‌ها: افزودن/حذف ادمین\n"
        "• عضویت اجباری: تعیین کانال\n"
        "• ممبرگیری: فعال‌سازی و تعیین نوع\n"
        "• مدیریت متن‌ها: تغییر متن‌های ربات\n"
      "• مدیریت دکمه‌ها: افزودن/حذف دکمه\n"
        "• مدیریت دوره‌ها: افزودن/حذف/ویرایش دوره\n"
        "• قفل دوره‌ها: تعیین نوع قفل\n"
        "• ارسال همگانی: ارسال پیام به همه کاربران\n"
        "• فوروارد همگانی: فوروارد پیام به همه\n"
        "• پیام خودکار: ارسال پیام زمان‌بندی شده\n"
        "• خروجی کاربران: دسته‌بندی بر اساس شهر\n"
        "• دستیار مدیران: تحلیل متن با هوش مصنوعی",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 برگشت", callback_data="admin_panel")]
        ])
    )
