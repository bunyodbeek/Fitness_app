from apps.models import UserProfile
from django.contrib import admin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'gender', 'age', 'weight', 'height', 'bmi', 'language']
    list_filter = ['gender', 'unit_system', 'language']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['age', 'bmi', 'created_at', 'updated_at']
