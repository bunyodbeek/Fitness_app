from django.db.models.aggregates import Count

from apps.models import Exercise
from apps.models.base import CreatedBaseModel
from django.db.models import (
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKey,
    ImageField,
    IntegerField,
    Model,
    TextField,
)
from django.utils.translation import gettext_lazy as _


class Program(CreatedBaseModel):
    title = CharField(max_length=200)
    description = TextField(blank=True)
    image = ImageField(upload_to='programs/')
    is_active = BooleanField(default=True)

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.title

    @property
    def exercises_count(self):
        return self.editions \
            .annotate(ex_count=Count('edition_exercises')) \
            .aggregate(total=Count('edition_exercises'))['total'] or 0


class Edition(Model):
    program = ForeignKey('apps.Program', CASCADE, related_name='editions')
    title = CharField(max_length=200)
    order = CharField(default=0)
    duration_weeks = CharField(help_text="Dastur davomiyligi (haftalarda)")
    days_per_week = CharField(default=3, help_text="Haftasiga necha kun")
    is_premium = BooleanField(_("Premium"), default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.program.title} - {self.title}"


class EditionExercise(CreatedBaseModel):
    edition = ForeignKey('apps.Edition', CASCADE, related_name='edition_exercises')
    exercise = ForeignKey('apps.Exercise', CASCADE, related_name='edition_exercises')
    order = IntegerField(default=0)
    sets = IntegerField(default=0, null=True, blank=True)
    reps = IntegerField(default=0, null=True, blank=True)
    minutes = IntegerField(default=0, null=True, blank=True)
    day_number = IntegerField(default=1, null=True, blank=True)

    class Meta:
        verbose_name = "Edition Exercise"
        verbose_name_plural = "Edition Exercises"


class Workout(Model):
    user = ForeignKey('apps.UserProfile', CASCADE, related_name="workouts")
    edition = ForeignKey('apps.Edition', SET_NULL, null=True, blank=True, related_name="workouts")

    started_at = DateTimeField(auto_now_add=True)
    finished_at = DateTimeField(null=True, blank=True)

    duration = IntegerField(default=0)
    calories = IntegerField(default=0)
    day_number = IntegerField(default=1)


class WorkoutExercise(Model):
    workout = ForeignKey('apps.Workout', CASCADE, related_name="workout_exercises")
    exercise = ForeignKey(Exercise, SET_NULL, null=True)

    sets = IntegerField(default=0)
    reps = IntegerField(default=0)
    weight = FloatField(default=0)

    order = IntegerField(default=0)
