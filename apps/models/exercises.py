# models/exercise.py

from django.db import models
from django.db.models import (
    CharField, ImageField, IntegerField,
    Model, FileField, DateTimeField,
    TextField, ForeignKey, CASCADE, FloatField
)


class MuscleGroup(Model):
    name = CharField(max_length=100)
    name_uz = CharField(max_length=100, blank=True)
    image = ImageField(upload_to='muscle_groups/', blank=True, null=True)
    order = IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "Mushak guruhi"
        verbose_name_plural = "Mushak guruhlari"

    def __str__(self):
        return self.name


class Exercise(Model):
    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', "Boshlang'ich"
        INTERMEDIATE = 'intermediate', "O'rta"
        ADVANCED = 'advanced', 'Murakkab'


    name = CharField(max_length=200, verbose_name="Nomi")
    name_uz = CharField(max_length=200, blank=True, verbose_name="O'zbek nomi")
    muscle_group = ForeignKey(
        MuscleGroup,
        on_delete=CASCADE,
        related_name='exercises',
        verbose_name="Mushak guruhi"
    )
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
    equipment = CharField(max_length=200, blank=True, verbose_name="Asboblar")

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Mashq"
        verbose_name_plural = "Mashqlar"

    def __str__(self):
        return self.name


class ExerciseInstruction(Model):
    """Mashq ko'rsatmalari"""
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


class BodyPart(Model):
    """Tana qismlari - dinamik nuqtalar uchun"""

    class Side(models.TextChoices):
        FRONT = 'front', 'Old tomon'
        BACK = 'back', 'Orqa tomon'
        BOTH = 'both', 'Ikkala tomon'

    name = CharField(max_length=100, verbose_name="Nomi")
    name_uz = CharField(max_length=100, blank=True, verbose_name="O'zbek nomi")

    # Front side pozitsiyasi (%)
    position_top = FloatField(default=0, verbose_name="Top pozitsiya (front %)")
    position_left = FloatField(default=0, verbose_name="Left pozitsiya (front %)")

    # Back side pozitsiyasi (%)
    back_position_top = FloatField(null=True, blank=True, default=0, verbose_name="Top pozitsiya (back %)")
    back_position_left = FloatField(null=True, blank=True, default=0, verbose_name="Left pozitsiya (back %)")

    # Label pozitsiyasi
    label_top = FloatField(null=True, blank=True, default=0, verbose_name="Label top %")
    label_left = FloatField(null=True, blank=True, default=0, verbose_name="Label left %")
    back_label_top = FloatField(null=True, blank=True, default=0, verbose_name="Back label top %")
    back_label_left = FloatField(null=True, blank=True, default=0, verbose_name="Back label left %")

    side = CharField(
        max_length=10,
        choices=Side.choices,
        default=Side.FRONT,
        verbose_name="Tomon"
    )

    muscle_group = ForeignKey(
        MuscleGroup,
        on_delete=CASCADE,
        related_name='body_parts',
        verbose_name="Mushak guruhi"
    )

    order = IntegerField(default=0, verbose_name="Tartib")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Tana qismi"
        verbose_name_plural = "Tana qismlari"

    def __str__(self):
        return self.name
