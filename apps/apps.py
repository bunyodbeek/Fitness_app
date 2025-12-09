from django.apps import AppConfig
from root.settings import BOT_TOKEN, WEBAPP_URL


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        """
        Django ishga tushishi bilan avtomatik webhook o‘rnatadi.
        """

        if not BOT_TOKEN or not WEBAPP_URL:
            print("❌ BOT_TOKEN yoki WEBHOOK_URL topilmadi (.env ni tekshiring)")
            return
