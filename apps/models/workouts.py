from apps.models.base import CreatedBaseModel
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    FloatField,
    ForeignKey,
    ImageField,
    IntegerField,
    Model,
    Sum,
    TextField,
)
from django.db.models.aggregates import Count
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
        return self.editions.annotate(ex_count=Count('workouts')) \
            .aggregate(total=Sum('ex_count'))['total'] or 0


class Edition(Model):
    program = ForeignKey('apps.Program', CASCADE, related_name='editions')
    title = CharField(max_length=200)
    order = CharField(default=0)
    duration_weeks = CharField(help_text="Dastur davomiyligi (haftalarda)")
    days_per_week = CharField(default=3, help_text="Haftasiga necha kun")
    is_premium = BooleanField(_("Premium"), default=True)

    class Meta:
        ordering = ['order']

    @property
    def exercises_count(self):
        return WorkoutExercise.objects.filter(
            workout__edition=self
        ).count()

    def __str__(self):
        return f"{self.program.title} - {self.title}"


class Workout(CreatedBaseModel):
    edition = ForeignKey('apps.Edition', CASCADE, related_name='workouts')
    day_number = IntegerField(default=1)
    title = CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Workout"
        verbose_name_plural = "Workouts"
        ordering = ['day_number']

    def __str__(self):
        return f"{self.edition.title} - Day {self.day_number}"


class WorkoutExercise(Model):
    workout = ForeignKey('apps.Workout', CASCADE, related_name="workout_exercises")
    exercise = ForeignKey('apps.Exercise', CASCADE, related_name="workout_exercises")

    sets = IntegerField(default=0)
    reps = IntegerField(default=0)
    weight = FloatField(default=0, null=True, blank=True)
    minutes = IntegerField(default=0, null=True, blank=True)

    order = IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.workout} - {self.exercise}"
