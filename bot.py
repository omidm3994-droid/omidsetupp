ᵒᵐᵢᵈ, [Aug 10, 2026 at 17:41]
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# -----------------------------
# ماژول‌ها
# -----------------------------
from modules.registration import start_registration, registration_handler
from modules.menu import send_main_menu
from modules.courses import open_courses_menu, course_selected
from modules.ai_chat import (
    start_ai_chat,
    ai_text_handler,
    ai_image_handler,
    ai_message_handler
)
from modules.referral import referral_menu, check_referral
from modules.locks import (
    lock_course_menu,
    lock_type_menu,
    lock_referral,
    lock_payment,
    lock_value_handler,
    receive_fish,
    fish_ok,
    fish_no
)
from modules.admin_panel import (
    admin_panel,
    admin_stats,
    admin_manage_admins,
    admin_add,
    admin_add_handler,
    admin_remove,
    admin_remove_handler,
    admin_force_join,
    force_on,
    force_off,
    force_set_channel,
    force_set_channel_handler,
    admin_texts,
    text_edit,
    text_edit_handler,
    admin_buttons,
    btn_add,
    btn_add_handler,
    btn_remove,
    btn_remove_handler,
    admin_courses,
    course_add,
    course_add_handler,
    course_remove,
    course_remove_handler,
    course_edit_title,
    course_edit_title_handler,
    admin_broadcast,
    admin_broadcast_handler,
    admin_forward,
    admin_forward_handler,
    admin_auto_msg,
    admin_auto_msg_handler,
    admin_export,
    admin_ai,
    admin_ai_handler,
    admin_help
)

# -----------------------------
# توکن ربات
# -----------------------------
TOKEN = os.getenv("8743511615:AAEmKgkD2u8qamEVfJ4Weiw2ExkL6FpRB-I")

app = Application.builder().token(TOKEN).build()


# -----------------------------
# هندلرهای ثبت‌نام
# -----------------------------
app.add_handler(CommandHandler("start", start_registration))
app.add_handler(MessageHandler(filters.TEXT, registration_handler))


# -----------------------------
# منوی اصلی
# -----------------------------
app.add_handler(CallbackQueryHandler(send_main_menu, pattern="^back_main$"))


# -----------------------------
# منوی آموزشی
# -----------------------------
app.add_handler(CallbackQueryHandler(open_courses_menu, pattern="^edu$"))
app.add_handler(CallbackQueryHandler(course_selected, pattern="^course_"))


# -----------------------------
# هوش مصنوعی
# -----------------------------
app.add_handler(CallbackQueryHandler(start_ai_chat, pattern="^ai$"))
app.add_handler(CallbackQueryHandler(ai_text_handler, pattern="^ai_text$"))
app.add_handler(CallbackQueryHandler(ai_image_handler, pattern="^ai_image$"))
app.add_handler(MessageHandler(filters.TEXT, ai_message_handler))


# -----------------------------
# ممبرگیری حرفه‌ای
# -----------------------------
app.add_handler(MessageHandler(filters.TEXT, check_referral))
app.add_handler(CallbackQueryHandler(referral_menu, pattern="^referral$"))


# -----------------------------
# قفل دوره‌ها
# -----------------------------
app.add_handler(CallbackQueryHandler(lock_course_menu, pattern="^lock_course$"))
app.add_handler(CallbackQueryHandler(lock_type_menu, pattern="^lock_select_"))
app.add_handler(CallbackQueryHandler(lock_referral, pattern="^lock_referral$"))
app.add_handler(CallbackQueryHandler(lock_payment, pattern="^lock_payment$"))
app.add_handler(MessageHandler(filters.TEXT, lock_value_handler))

app.add_handler(CallbackQueryHandler(receive_fish, pattern="^send_fish_"))
app.add_handler(CallbackQueryHandler(fish_ok, pattern="^fish_ok_"))
app.add_handler(CallbackQueryHandler(fish_no, pattern="^fish_no_"))


# -----------------------------
# پنل مدیریت
# -----------------------------
app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin_panel$"))
app.add_handler(CallbackQueryHandler(admin_stats, pattern="^admin_stats$"))
app.add_handler(CallbackQueryHandler(admin_manage_admins, pattern="^admin_manage_admins$"))

app.add_handler(CallbackQueryHandler(admin_add, pattern="^admin_add$"))
app.add_handler(MessageHandler(filters.TEXT, admin_add_handler))

app.
