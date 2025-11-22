from django.apps import AppConfig

from root.settings import BOT_TOKEN, WEBAPP_URL


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'

    def ready(self):
        """
        Django ishga tushishi bilan avtomatik webhook o‘rnatadi.
        """

        from telebot import TeleBot

        if not BOT_TOKEN or not WEBAPP_URL:
            print("❌ BOT_TOKEN yoki WEBHOOK_URL topilmadi (.env ni tekshiring)")
            return
        #
        # bot = TeleBot(BOT_TOKEN)
        #
        # # # bot.set_my_description('darslik haqida')
        # # # Avval eski webhook o'chiriladi, keyin yangi o'rnatiladi
        #
        # bot.remove_webhook()
        # status = bot.set_webhook(WEBAPP_URL + '/bot/webhook/')
        #
        # if status:
        #     print(f"✅ Webhook o‘rnatildi: {WEBAPP_URL}/bot/webhook/")
        # else:
        #     print("❌ Webhookni o‘rnatishda xatolik yuz berdi")
