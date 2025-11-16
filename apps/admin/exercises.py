from apps.models import Exercise, ExerciseInstruction
from django.contrib import admin


class ExerciseInstructionInline(admin.TabularInline):
    model = ExerciseInstruction
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'primary_body_part', 'difficulty']
    list_filter = ['primary_body_part', 'difficulty']
    search_fields = ['name', 'name_uz']
    inlines = [ExerciseInstructionInline]
