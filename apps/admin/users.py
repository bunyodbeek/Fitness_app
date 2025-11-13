from apps.models import PaymentHistory, UserProfile
from django.contrib import admin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'gender', 'age', 'weight', 'height', 'bmi', 'language', 'is_subscribed']
    list_filter = ['gender', 'unit_system', 'language']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['age', 'bmi', 'is_subscribed', 'created_at', 'updated_at']

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('user', 'name', 'avatar', 'gender', 'birth_date', 'age')
        }),
        ('Tana o\'lchamlari', {
            'fields': ('weight', 'height', 'bmi', 'unit_system')
        }),
        ('Sozlamalar', {
            'fields': ('language',)
        }),
        ('Obuna', {
            'fields': ('subscription_start_date', 'subscription_end_date', 'payment_method',
                       'subscription_price', 'is_subscribed', 'days_until_renewal')
        }),
        ('Qo\'shimcha', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'transaction_id']
    readonly_fields = ['created_at']
