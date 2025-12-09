from apps.models import Favorite, UserProfile
from apps.models.favorites import FavoriteCollection
from django.contrib import admin


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'gender', 'age', 'weight', 'height', 'bmi', 'language']
    list_filter = ['gender', 'unit_system', 'language']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['age', 'bmi', 'created_at', 'updated_at']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise']


@admin.register(FavoriteCollection)
class FavoriteCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'exercise_count', 'created_at']
    list_filter = ['created_at']
    # filter_horizontal = ['exercises']
