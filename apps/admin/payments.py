from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.models import Subscription, PaymentMethod, Payment


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Obunalar uchun admin panel
    """
    list_display = [
        'user',
        'start_date',
        'end_date',
        'is_active',
        'auto_renew',
        'price',
        'days_remaining_display',
    ]

    list_filter = [
        'is_active',
        'auto_renew',
        'start_date',
        'end_date'
    ]

    date_hierarchy = 'start_date'

    readonly_fields = [
        'start_date',
        'days_remaining_display',
        'progress_display',
    ]

    fieldsets = (
        (_('Asosiy ma\'lumotlar'), {
            'fields': ('user', 'start_date', 'end_date', 'price')
        }),
        (_('Holat'), {
            'fields': (
                'is_active',
            )
        }),
        (_('Avtomatik to\'lov'), {
            'fields': ('failed_payment_attempts', 'last_failed_payment')
        }),
    )

    def days_remaining_display(self, obj):
        """Qolgan kunlarni ko'rsatish"""
        return f"{obj.days_remaining()} kun"

    days_remaining_display.short_description = _("Qolgan kunlar")

    def progress_display(self, obj):
        """Progress foizini ko'rsatish"""
        return f"{obj.progress_percentage()}%"

    progress_display.short_description = _("Progress")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    To'lov usullari uchun admin panel
    """
    list_display = [
        'user',
        'card_type',
        'masked_card_display',
        'expiry_display',
        'is_expired_display',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'card_type',
        'is_active',
        'created_at'
    ]

    search_fields = [
        'user__username',
        'user__email',
        'card_last_four'
    ]

    readonly_fields = [
        'card_token',
        'created_at',
        'updated_at',
        'is_expired_display'
    ]

    fieldsets = (
        (_('Foydalanuvchi'), {
            'fields': ('user',)
        }),
        (_('Karta ma\'lumotlari'), {
            'fields': (
                'card_type',
                'card_token',
                'card_last_four',
                'expiry_month',
                'expiry_year',
                'is_active'
            )
        }),
        (_('Vaqt'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def masked_card_display(self, obj):
        """Kartani yashirib ko'rsatish"""
        return f"****{obj.card_last_four}"

    masked_card_display.short_description = _("Karta")

    def expiry_display(self, obj):
        """Amal qilish muddatini ko'rsatish"""
        return f"{obj.expiry_month}/{obj.expiry_year}"

    expiry_display.short_description = _("Amal qilish")

    def is_expired_display(self, obj):
        """Muddati tugaganligini ko'rsatish"""
        return obj.is_expired()

    is_expired_display.boolean = True
    is_expired_display.short_description = _("Muddati tugagan")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    To'lovlar uchun admin panel
    """
    list_display = [
        'user',
        'payment_type',
        'amount',
        'status',
        'is_auto_payment',
        'auto_payment_attempt',
        'created_at',
        'completed_at'
    ]

    list_filter = [
        'payment_type',
        'status',
        'is_auto_payment',
        'created_at'
    ]

    search_fields = [
        'user__username',
        'user__email',
        'transaction_id',
        'click_trans_id'
    ]

    date_hierarchy = 'created_at'

    readonly_fields = [
        'created_at',
        'transaction_id',
        'click_trans_id',
        'metadata'
    ]

    fieldsets = (
        (_('To\'lov ma\'lumotlari'), {
            'fields': (
                'user',
                'subscription',
                'payment_type',
                'amount',
                'transaction_id',
                'click_trans_id'
            )
        }),
        (_('Holat'), {
            'fields': (
                'status',
                'created_at',
                'completed_at'
            )
        }),
        (_('Avtomatik to\'lov'), {
            'fields': (
                'is_auto_payment',
                'auto_payment_attempt'
            )
        }),
        (_('Qo\'shimcha ma\'lumotlar'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """To'lovlarni faqat superuser o'chirishi mumkin"""
        return request.user.is_superuser
