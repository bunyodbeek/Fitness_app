from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    BigIntegerField,
    BooleanField,
    CharField,
    DateField,
    DecimalField,
    ForeignKey,
    ImageField,
    IntegerField,
    OneToOneField,
    TextChoices,
    TextField,
)

from apps.models.base import CreatedBaseModel


class User(AbstractUser):
    pass


class UserProfile(CreatedBaseModel):
    class Gender(TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'

    class UnitSystem(TextChoices):
        METRIC = 'metric', 'Metric'
        ENGLISH = 'english', 'English'

    class Language(TextChoices):
        UZBEK = 'uz', "O'zbekcha"
        ENGLISH = 'en', 'English'
        RUSSIAN = 'ru', 'Русский'

    class ExperienceLevel(TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    class FitnessGoal(TextChoices):
        BUILD_BODY = 'build_body', 'Build a great body'
        LOSE_WEIGHT = 'lose_weight', 'Lose weight'
        GAIN_MUSCLE = 'gain_muscle', 'Gain muscle'
        GET_SHAPE = 'get_shape', 'Get in shape'

    user = OneToOneField('apps.User', CASCADE, related_name='profile')
    telegram_id = BigIntegerField(unique=True, null=True, blank=True)
    is_premium = BooleanField(default=False)
    name = CharField(max_length=100, default='User')
    avatar = ImageField(upload_to='avatars/', blank=True, null=True)
    gender = CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    birth_date = DateField(null=True, blank=True)
    weight = DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height = DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    experience_level = CharField(max_length=20, choices=ExperienceLevel.choices, blank=True)
    fitness_goal = CharField(max_length=20, choices=FitnessGoal.choices, blank=True)
    workout_days_per_week = IntegerField(null=True, blank=True)
    unit_system = CharField(max_length=10, choices=UnitSystem.choices, default=UnitSystem.METRIC)
    language = CharField(max_length=5, choices=Language.choices, default=Language.UZBEK)
    onboarding_completed = BooleanField(default=False)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.name}"

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            is_before_birthday = (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            return today.year - self.birth_date.year - int(is_before_birthday)
        return None

    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None


class UserMotivation(CreatedBaseModel):
    class MotivationType(TextChoices):
        HEALTHY_LIFESTYLE = 'healthy_lifestyle', 'I want a healthy lifestyle'
        IMPROVE_PHYSIQUE = 'improve_physique', 'Improve my physique'
        GET_STRONGER = 'get_stronger', 'Get stronger every day'
        GOOD_CHALLENGE = 'good_challenge', 'I like a good challenge'

    user = ForeignKey('apps.UserProfile', CASCADE, related_name='motivations')
    motivation = CharField(max_length=30, choices=MotivationType.choices)

    class Meta:
        unique_together = ['user', 'motivation']
        verbose_name = "User Motivation"
        verbose_name_plural = "User Motivations"

    def __str__(self):
        return f"{self.user.name} - {self.get_motivation_display()}"


class PaymentHistory(CreatedBaseModel):
    class PaymentStatus(TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        COMPLETED = 'completed', 'To langan'
        FAILED = 'failed', 'Muvaffaqiyatsiz'
        REFUNDED = 'refunded', 'Qaytarilgan'

    user = ForeignKey('apps.UserProfile', CASCADE, related_name='payment_history')
    amount = DecimalField(max_digits=10, decimal_places=2)
    payment_method = CharField(max_length=50)
    status = CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = CharField(max_length=100, blank=True)
    description = TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "To'lov tarixi"
        verbose_name_plural = "To'lovlar tarixi"

    def __str__(self):
        return f"{self.user.name} - {self.amount} UZS - {self.get_status_display()}"
