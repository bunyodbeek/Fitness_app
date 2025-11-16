from django.db.models import (
    CASCADE,
    CharField,
    FileField,
    ForeignKey,
    ImageField,
    IntegerField,
    Model,
    TextChoices,
    TextField, )
from django.utils.translation import gettext_lazy as _

from apps.models.base import CreatedBaseModel


class MuscleGroup(TextChoices):
    SHOULDERS = "shoulders", "Shoulders"
    CHEST = "chest", "Chest"
    BICEPS = "biceps", "Biceps"
    FOREARM = "forearm", "Forearm"
    ABS = "abs", "Abs"
    OBLIQUES = "obliques", "Obliques"
    QUADS = "quads", "Quadriceps"
    ADDUCTORS = "adductors", "Adductors (Inner Thigh)"
    ABDUCTORS = "abductors", "Abductors (Outer Thigh)"

    TRAPS = "traps", "Trapezius"
    TRICEPS = "triceps", "Triceps"
    LATS = "lats", "Latissimus Dorsi"
    LOWER_BACK = "lower_back", "Lower Back"
    GLUTES = "glutes", "Glutes"
    HAMSTRINGS = "hamstrings", "Hamstrings"
    CALVES = "calves", "Calves"

    CARDIO = "cardio", "Cardio"


class Exercise(CreatedBaseModel):
    class Difficulty(TextChoices):
        BEGINNER = 'beginner', _("Beginner")
        INTERMEDIATE = 'intermediate', _("Intermediate")
        ADVANCED = 'advanced', _('Advanced')

    name = CharField(_("Name"), max_length=200)
    name_uz = CharField(_("Uzbek Name"), max_length=200, blank=True)
    primary_body_part = CharField(_("Muscle Group"), choices=MuscleGroup.choices, default=MuscleGroup.SHOULDERS)
    secondary_body_part = CharField(_("Secondary Muscle"), choices=MuscleGroup.choices, null=True, blank=True)
    description = TextField(_("Description"), blank=True)
    thumbnail = ImageField(_("Image"), upload_to='exercises/thumbnails/', blank=True, null=True)
    video = FileField(upload_to='exercises/videos/', blank=True, null=True)
    difficulty = CharField(_("Difficulty"), max_length=20, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE)

    class Meta:
        ordering = ['name']
        verbose_name = _("Exercise")
        verbose_name_plural = _("Exercises")

    def __str__(self):
        return self.name


class ExerciseInstruction(Model):
    exercise = ForeignKey('apps.Exercise', CASCADE, related_name='instructions', verbose_name=_("Exercise"))
    step_number = IntegerField(_("Stem Number"), default=1)
    text = TextField(_("Text"), blank=True)
    text_uz = TextField(_("Uzbek Text"), blank=True)

    class Meta:
        ordering = ['step_number']
        unique_together = ('exercise', 'step_number')
        verbose_name = _("ExerciseInstruction")
        verbose_name_plural = _("ExerciseInstructions")

    def __str__(self):
        return f"{self.exercise.name} - Qadam {self.step_number}"
