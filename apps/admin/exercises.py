from apps.models import Exercise, ExerciseInstruction
from django.contrib import admin


class ExerciseInstructionInline(admin.TabularInline):
    model = ExerciseInstruction
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "primary_body_part", "calory")
    list_filter = ("primary_body_part",)
    search_fields = ("name",)



