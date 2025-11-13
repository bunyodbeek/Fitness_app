from django.contrib import admin

from apps.models import UserActivity


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'created_at']
    list_filter = ['event', 'created_at']
    search_fields = ['user__telegram_id']
    readonly_fields = ['created_at']
