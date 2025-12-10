from datetime import timedelta

from dateutil.relativedelta import relativedelta
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
    IntegerField, )
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreatedBaseModel


class SubscriptionPlan(Model):
    class PeriodChoices(TextChoices):
        MONTHLY = 'monthly', "1 oylik"
        QUARTERLY = 'quarterly', "3 oylik"
        YEARLY = 'yearly', "1 yillik"


    price = DecimalField(max_digits=10, decimal_places=2)
    period = CharField(max_length=20, choices=PeriodChoices.choices)

    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.get_period_display()}"

    def get_expiry_date(self, start_date):
        if self.period == 'monthly':
            return start_date + relativedelta(months=1)
        elif self.period == 'quarterly':
            return start_date + relativedelta(months=3)
        elif self.period == 'yearly':
            return start_date + relativedelta(years=1)
        return 0

    def period_days(self) -> int:
        if self.period == 'monthly':
            return 30
        elif self.period == 'quarterly':
            return 90
        elif self.period == 'yearly':
            return 365
        return 0



class Subscription(Model):
    user = OneToOneField('apps.UserProfile', CASCADE, related_name='subscription', verbose_name=_("User"))
    plan = ForeignKey('apps.SubscriptionPlan', CASCADE, related_name='subscriptions')
    start_date = DateTimeField(_("Start Date"), auto_now_add=True)
    end_date = DateTimeField(_("End Date"))
    is_active = BooleanField(_("Is Active"), default=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            start = self.start_date or timezone.now()
            self.end_date = self.plan.get_expiry_date(start)
        super().save(*args, **kwargs)


    def period(self):
        return self.plan.period_days()

    def days_remaining(self) -> int:
        if not self.is_active or not self.end_date:
            return 0
        delta: timedelta = self.end_date - timezone.now()
        return max(0, delta.days)


    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.user.name} - Premium"


class Payment(CreatedBaseModel):
    class PaymentStatus(TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        COMPLETED = 'completed', 'Bajarildi'
        FAILED = 'failed', 'Muvaffaqiyatsiz'
        REFUNDED = 'refunded', 'Qaytarildi'

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
        self.status = self.PaymentStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save()

    def mark_as_failed(self):
        self.status = self.PaymentStatus.FAILED
        self.save()
