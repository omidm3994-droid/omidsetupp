from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 فایل‌های آموزشی", callback_data="edu")],
        [InlineKeyboardButton("🤖 دستیار هوش مصنوعی", callback_data="ai")],
        [InlineKeyboardButton("🛠 پشتیبانی", callback_data="support")],
        [InlineKeyboardButton("📅 نوبت‌دهی", callback_data="appointment")],
    ]

    await update.message.reply_text(
        "منوی اصلی 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
