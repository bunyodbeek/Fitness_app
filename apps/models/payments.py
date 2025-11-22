from apps.models.base import CreatedBaseModel
from django.db.models import (
    CASCADE,
    SET_NULL,
    ForeignKey,
    JSONField,
    Model,
    OneToOneField,
    TextChoices,
)
from django.db.models.fields import (
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    IntegerField,
)
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PaymentStatus(TextChoices):
    PENDING = 'pending', 'Kutilmoqda'
    COMPLETED = 'completed', 'Bajarildi'
    FAILED = 'failed', 'Muvaffaqiyatsiz'
    REFUNDED = 'refunded', 'Qaytarildi'


class Subscription(Model):
    user = OneToOneField('apps.UserProfile', CASCADE, related_name='subscription', verbose_name=_("User"))
    start_date = DateTimeField(_("Start Date"), auto_now_add=True)
    end_date = DateTimeField(_("End Date"))
    is_active = BooleanField(_("Is Active"), default=True)
    auto_renew = BooleanField(_("Auto Renew"), default=True)
    price = DecimalField(_("monthly payment price"), max_digits=10, decimal_places=2, default=67000.00)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.name} - Premium"

    def days_remaining(self):
        if not self.is_active:
            return 0
        delta = self.end_date - timezone.now()
        return max(0, delta.days)


class Payment(CreatedBaseModel):
    user = ForeignKey("apps.UserProfile", CASCADE, related_name='payments', verbose_name=_("User"))
    subscription = ForeignKey('apps.Subscription', SET_NULL, null=True, related_name='payments',
                              verbose_name=_("Subscription"))
    status = CharField(_("Status"), max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    click_trans_id = CharField(_("Click Transaction ID"), max_length=100, blank=True, null=True)
    transaction_id = CharField(_("Merchant Transaction ID"), max_length=100, unique=True, blank=True, null=True)
    is_auto_payment = BooleanField(_("Is Auto Payment"), default=False)
    auto_payment_attempt = IntegerField(_("Automatic payment attempt"), default=0)
    metadata = JSONField(_("Additional Information"), default=dict, blank=True)
    completed_at = DateTimeField(_("Completed Date"), blank=True, null=True)

    class Meta:
        verbose_name = _("To'lov")
        verbose_name_plural = _("To'lovlar")

    def mark_as_completed(self):
        self.status = PaymentStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def mark_as_failed(self):
        self.status = PaymentStatus.FAILED
        self.save()
