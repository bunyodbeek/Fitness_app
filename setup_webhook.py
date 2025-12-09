import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from apps.bot.utils import setup_webhook
from root.settings import BOT_TOKEN, WEBAPP_URL

setup_webhook(BOT_TOKEN, WEBAPP_URL)
