# bot_runner.py - ODDIY VERSIYA

import logging
import os

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# .env faylni yuklash
load_dotenv()

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command - Mini App tugmasini ko'rsatish
    """
    user = update.effective_user

    # Mini App URL
    webapp_url = os.getenv('WEBAPP_URL', 'https://educated-luana-shroudlike.ngrok-free.dev')

    # Mini App tugmasi
    webapp = WebAppInfo(url=webapp_url + '/miniapp/questionnaire/')
    keyboard = [
        [KeyboardButton(text="🏋️ Start Fitness Journey", web_app=webapp)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"💪 Welcome {user.first_name}!\n\n"
        "Ready to transform your body?\n\n"
        "Tap the button below to create your personalized workout plan! 🚀",
        reply_markup=reply_markup
    )

    logger.info(f"User {user.id} ({user.first_name}) started bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "🏋️ Fitness Bot Commands:\n\n"
        "/start - Begin your fitness journey\n"
        "/help - Show this message"
    )


def main():
    """Bot'ni ishga tushirish"""

    # Token olish
    bot_token = os.getenv('BOT_TOKEN')
    webapp_url = os.getenv('WEBAPP_URL')

    print("🤖 Telegram Bot starting...")
    print(f"BOT_TOKEN: {bot_token}")
    print(f"WEBAPP_URL: {webapp_url}")

    if not bot_token:
        print("❌ BOT_TOKEN not found in .env file!")
        return

    # Application yaratish
    application = Application.builder().token(bot_token).build()

    # Handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Bot ishga tushirish
    print("✅ Bot started successfully!")
    print("👉 Open Telegram and send /start")
    print("📱 Press Ctrl+C to stop\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
