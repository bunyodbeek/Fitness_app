from apps.models.workouts import Edition, Program, Workout, WorkoutExercise, WorkoutProgress
from django.contrib import admin


class WorkoutInline(admin.TabularInline):
    model = Workout
    extra = 1


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1

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
    inlines = [WorkoutInline]


@admin.register(WorkoutProgress)
class WorkoutProgressAdmin(admin.ModelAdmin):
    pass


@admin.register(Workout)
class WorkoutModelAdmin(admin.ModelAdmin):
    inlines = [WorkoutExerciseInline]

