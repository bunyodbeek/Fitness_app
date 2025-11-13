from django.contrib import admin

from apps.models import Program, Edition, Workout, WorkoutExercise


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


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    fields = ['order', 'exercise', 'sets', 'reps', 'duration_type', 'duration_seconds', 'rest_seconds']
    autocomplete_fields = ['exercise']


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['edition', 'day_number', 'title', 'total_exercises']
    list_filter = ['edition__program', 'edition']
    search_fields = ['title']
    inlines = [WorkoutExerciseInline]


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ['workout', 'exercise', 'order', 'sets', 'reps', 'rest_seconds']
    list_filter = ['workout__edition__program']
    search_fields = ['exercise__name', 'workout__title']
    autocomplete_fields = ['exercise']
