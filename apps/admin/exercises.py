from apps.models import Exercise, ExerciseInstruction
from django.contrib import admin


class ExerciseInstructionInline(admin.TabularInline):
    model = ExerciseInstruction
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'difficulty']
    list_filter = ['muscle_group', 'difficulty']
    search_fields = ['name', 'name_uz']
    inlines = [ExerciseInstructionInline]
