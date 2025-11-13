from django.db.models import (
    CASCADE,
    CharField,
    FileField,
    ForeignKey,
    ImageField,
    IntegerField,
    Model,
    TextField, TextChoices,
)

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
        BEGINNER = 'beginner', "Boshlang'ich"
        INTERMEDIATE = 'intermediate', "O'rta"
        ADVANCED = 'advanced', 'Murakkab'

    name = CharField(max_length=200, verbose_name="Nomi")
    name_uz = CharField(max_length=200, blank=True, verbose_name="O'zbek nomi")
    muscle_group = CharField(choices=MuscleGroup.choices, default=MuscleGroup.SHOULDERS)
    description = TextField(blank=True, verbose_name="Tavsif")

    thumbnail = ImageField(upload_to='exercises/thumbnails/', blank=True, null=True, verbose_name="Rasm")
    detail_image = ImageField(upload_to='exercises/details/', blank=True, null=True, verbose_name="Batafsil rasm")
    video = FileField(upload_to='exercises/videos/', blank=True, null=True, verbose_name="Video")

    difficulty = CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.INTERMEDIATE,
        verbose_name="Qiyinlik darajasi"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "Mashq"
        verbose_name_plural = "Mashqlar"

    def __str__(self):
        return self.name


class ExerciseInstruction(Model):
    exercise = ForeignKey(
        Exercise,
        on_delete=CASCADE,
        related_name='instructions',
        verbose_name="Mashq"
    )
    step_number = IntegerField(verbose_name="Qadam raqami")
    text = TextField(verbose_name="Matn")
    text_uz = TextField(blank=True, verbose_name="O'zbek matn")

    class Meta:
        ordering = ['step_number']
        unique_together = ('exercise', 'step_number')
        verbose_name = "Mashq ko'rsatmasi"
        verbose_name_plural = "Mashq ko'rsatmalari"

    def __str__(self):
        return f"{self.exercise.name} - Qadam {self.step_number}"
