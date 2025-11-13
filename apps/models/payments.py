from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import (
    Model, OneToOneField, ForeignKey, CASCADE, SET_NULL, JSONField
)
from django.db.models.fields import (
    DateTimeField, BooleanField, DecimalField, IntegerField, CharField
)
from django.utils.translation import gettext_lazy as _


class CardType(models.TextChoices):
    UZCARD = 'uzcard', 'UzCard'
    HUMO = 'humo', 'Humo'


class PaymentType(models.TextChoices):
    SUBSCRIPTION_NEW = 'subscription_new', "Yangi obuna"
    SUBSCRIPTION_RENEW = 'subscription_renew', "Obuna yangilandi"
    SUBSCRIPTION_AUTO = 'subscription_auto', "Avtomatik to'lov"


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Kutilmoqda'
    COMPLETED = 'completed', 'Bajarildi'
    FAILED = 'failed', 'Muvaffaqiyatsiz'
    REFUNDED = 'refunded', 'Qaytarildi'


class Subscription(Model):
    user = OneToOneField('apps.User', CASCADE, related_name='subscription', verbose_name=_("Foydalanuvchi"))
    start_date = DateTimeField(_("Boshlanish sanasi"), auto_now_add=True)
    end_date = DateTimeField(_("Tugash sanasi"))
    is_active = BooleanField(_("Faolmi"), default=True)
    auto_renew = BooleanField(_("Avtomatik yangilash"), default=True)
    price = DecimalField(
        max_digits=10,
        decimal_places=2,
        default=67000.00,
        verbose_name=_("Oylik narx (UZS)")
    )

    class Meta:
        verbose_name = _("Obuna")
        verbose_name_plural = _("Obunalar")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.username} - Premium"

    def days_remaining(self):
        if not self.is_active:
            return 0
        delta = self.end_date - datetime.now()
        return max(0, delta.days)

    def progress_percentage(self):
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (datetime.now() - self.start_date).days
        if total_days <= 0:
            return 0
        return min(100, int((elapsed_days / total_days) * 100))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.has_premium = self.is_active
        self.user.premium_until = self.end_date
        self.user.save(update_fields=['has_premium', 'premium_until'])

    def increment_failed_payment(self):
        self.failed_payment_attempts += 1  # TODO if self.end_date > self.end_date + 3 kun and self.user.is_premium:
        self.last_failed_payment = datetime.now()
        self.save()

        if self.failed_payment_attempts >= 3:
            self.is_active = False
            self.auto_renew = False
            self.save()
            return True
        return False

    def reset_failed_attempts(self):
        self.failed_payment_attempts = 0
        self.last_failed_payment = None
        self.save()


class PaymentMethod(Model):
    user = OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='payment_method',
        verbose_name=_("Foydalanuvchi")
    )
    card_type = CharField(
        max_length=20,
        choices=CardType.choices,
        verbose_name=_("Karta turi")
    )
    card_token = CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Karta token (Click)")
    )
    card_last_four = CharField(
        max_length=4,
        verbose_name=_("Oxirgi 4 raqam")
    )
    expiry_month = CharField(
        max_length=2,
        verbose_name=_("Amal qilish oyi")
    )
    expiry_year = CharField(
        max_length=4,
        verbose_name=_("Amal qilish yili")
    )
    is_active = BooleanField(
        default=True,
        verbose_name=_("Faolmi")
    )
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("To'lov usuli")
        verbose_name_plural = _("To'lov usullari")

    def __str__(self):
        return f"{self.card_type} - ****{self.card_last_four}"

    def is_expired(self):
        from datetime import date
        current_year = date.today().year
        current_month = date.today().month

        card_year = int(self.expiry_year)
        card_month = int(self.expiry_month)

        if card_year < current_year:
            return True
        if card_year == current_year and card_month < current_month:
            return True
        return False


class Payment(Model):
    """To'lov tarixi - Click orqali"""
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='payments',
        verbose_name=_("Foydalanuvchi")
    )
    subscription = ForeignKey(
        Subscription,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name=_("Obuna")
    )
    payment_type = CharField(
        max_length=30,
        choices=PaymentType.choices,
        verbose_name=_("To'lov turi")
    )
    amount = DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Miqdor (UZS)")
    )
    status = CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_("Holat")
    )
    click_trans_id = CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Click Transaction ID")
    )
    transaction_id = CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Merchant Transaction ID")
    )
    is_auto_payment = BooleanField(
        default=False,
        verbose_name=_("Avtomatik to'lovmi")
    )
    auto_payment_attempt = IntegerField(
        default=0,
        verbose_name=_("Avtomatik to'lov urinishi")
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Qo'shimcha ma'lumotlar")
    )
    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name=_("Yaratilgan sana")
    )
    completed_at = DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Bajarilgan sana")
    )

    class Meta:
        verbose_name = _("To'lov")
        verbose_name_plural = _("To'lovlar")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} UZS - {self.get_payment_type_display()}"

    def mark_as_completed(self):
        """To'lovni bajarilgan deb belgilash"""
        self.status = PaymentStatus.COMPLETED
        self.completed_at = datetime.now()
        self.save()

        if self.is_auto_payment and self.subscription:
            self.subscription.reset_failed_attempts()

    def mark_as_failed(self):
        """To'lovni muvaffaqiyatsiz deb belgilash"""
        self.status = PaymentStatus.FAILED
        self.save()

        if self.is_auto_payment and self.subscription:
            self.subscription.increment_failed_payment()
