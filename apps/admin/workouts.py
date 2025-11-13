from apps.models import Edition, Program, Workout
from django.contrib import admin


class EditionInline(admin.TabularInline):
    model = Edition
    extra = 1
    fields = ['order', 'title', 'duration_weeks', 'days_per_week']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    inlines = [EditionInline]


class WorkoutInline(admin.TabularInline):
    model = Workout
    extra = 1
    fields = ['order', 'day_number', 'title']


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ['program', 'title', 'order', 'duration_weeks', 'days_per_week']
    list_filter = ['program']
    search_fields = ['title']
    inlines = [WorkoutInline]




