from django.contrib import admin

from apps.models import MuscleGroup, Exercise, ExerciseInstruction


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_uz', 'order']
    list_editable = ['order']


class ExerciseInstructionInline(admin.TabularInline):
    model = ExerciseInstruction
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'muscle_group', 'difficulty']
    list_filter = ['muscle_group', 'difficulty']
    search_fields = ['name', 'name_uz']
    inlines = [ExerciseInstructionInline]
