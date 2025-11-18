from django.contrib import admin

from apps.models.workouts import Edition, EditionExercise, Program


class EditionExerciseInline(admin.TabularInline):
    model = EditionExercise
    extra = 1
    fields = ("exercise", "sets", "reps", "order")
    ordering = ("order",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    list_filter = ()
    ordering = ("id",)


@admin.register(Edition)
class EditionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "program", "order")
    list_filter = ("program",)
    search_fields = ("title",)
    ordering = ("program", "order")
    inlines = [EditionExerciseInline]
