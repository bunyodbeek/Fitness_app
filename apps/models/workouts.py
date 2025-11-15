from apps.models import Exercise
from apps.models.base import CreatedBaseModel
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    ForeignKey,
    ImageField,
    IntegerField,
    Model,
)


class Program(CreatedBaseModel):
    title = CharField(max_length=200)
    description = CharField()
    image = ImageField(upload_to='programs/')
    is_active = BooleanField(default=True)

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.title


class Edition(Model):
    program = ForeignKey(Program, on_delete=CASCADE, related_name='editions')
    title = CharField(max_length=200)
    order = CharField(default=0)
    duration_weeks = CharField(help_text="Dastur davomiyligi (haftalarda)")
    days_per_week = CharField(default=3, help_text="Haftasiga necha kun")
    description = CharField()
    image = ImageField(upload_to='editions/', null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.program.title} - {self.title}"


class EditionExercise(CreatedBaseModel):
    edition = ForeignKey(Edition, on_delete=CASCADE, related_name='exercises')
    exercise = ForeignKey(Exercise, on_delete=CASCADE, related_name='exercises')
    sets = IntegerField(default=0, null=True, blank=True)
    reps = IntegerField(default=0, null=True, blank=True)
    minutes = IntegerField(default=0, null=True, blank=True)
    day_number = IntegerField(default=1)


    class Meta:
        verbose_name = "Edition Exercise"
        verbose_name_plural = "Edition Exercises"
