# apps/users/models.py

from datetime import date
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    TextChoices, Model, OneToOneField, BigIntegerField,
    DecimalField, CharField, TextField, DateTimeField,
    ForeignKey, CASCADE, BooleanField, ImageField,
    DateField, IntegerField
)


class User(AbstractUser):
    """Custom User modeli"""
    pass


# ===== TEXTCHOICES ENUMLAR =====
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


class MotivationType(TextChoices):
    HEALTHY_LIFESTYLE = 'healthy_lifestyle', 'I want a healthy lifestyle'
    IMPROVE_PHYSIQUE = 'improve_physique', 'Improve my physique'
    GET_STRONGER = 'get_stronger', 'Get stronger every day'
    GOOD_CHALLENGE = 'good_challenge', 'I like a good challenge'


class PaymentStatus(TextChoices):
    PENDING = 'pending', 'Kutilmoqda'
    COMPLETED = 'completed', 'To langan'
    FAILED = 'failed', 'Muvaffaqiyatsiz'
    REFUNDED = 'refunded', 'Qaytarilgan'


# ===== ASOSIY MODELLAR =====
class UserProfile(Model):
    """Foydalanuvchi profili (asosiy ma'lumotlar)"""
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='profile')

    # Telegram ma'lumotlari
    telegram_id = BigIntegerField(unique=True, null=True, blank=True)
    telegram_username = CharField(max_length=255, blank=True)
    is_premium = BooleanField(default=False)

    # Personal info
    name = CharField(max_length=100, default='User')
    avatar = ImageField(upload_to='avatars/', blank=True, null=True)
    gender = CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    birth_date = DateField(null=True, blank=True)

    # Body measurements
    weight = DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height = DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    # Onboarding ma'lumotlari
    experience_level = CharField(max_length=20, choices=ExperienceLevel.choices, blank=True)
    fitness_goal = CharField(max_length=20, choices=FitnessGoal.choices, blank=True)
    workout_days_per_week = IntegerField(null=True, blank=True)

    # Settings
    unit_system = CharField(max_length=10, choices=UnitSystem.choices, default=UnitSystem.METRIC)
    language = CharField(max_length=5, choices=Language.choices, default=Language.UZBEK)

    # Onboarding tugaganmi?
    onboarding_completed = BooleanField(default=False)

    # Subscription info
    subscription_start_date = DateField(null=True, blank=True)
    subscription_end_date = DateField(null=True, blank=True)
    payment_method = CharField(max_length=50, blank=True)
    subscription_price = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.name} - {self.telegram_id or 'no telegram'}"

    # ===== Properties =====
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                    (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def bmi(self):
        if self.weight and self.height:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

    @property
    def is_subscribed(self):
        return bool(self.subscription_end_date and self.subscription_end_date >= date.today())

    @property
    def days_until_renewal(self):
        """Obuna yangilanishiga qolgan kunlar"""
        if self.subscription_end_date:
            delta = self.subscription_end_date - date.today()
            return max(0, delta.days)
        return 0


class UserMotivation(Model):
    """Foydalanuvchi motivatsiyalari (ko'p tanlovli)"""
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='motivations')
    motivation = CharField(max_length=30, choices=MotivationType.choices)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'motivation']
        verbose_name = "User Motivation"
        verbose_name_plural = "User Motivations"

    def __str__(self):
        return f"{self.user.username} - {self.get_motivation_display()}"


class PaymentHistory(Model):
    """To'lovlar tarixi"""
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='payment_history')
    amount = DecimalField(max_digits=10, decimal_places=2)
    payment_method = CharField(max_length=50)
    status = CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = CharField(max_length=100, blank=True)
    description = TextField(blank=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "To'lov tarixi"
        verbose_name_plural = "To'lovlar tarixi"

    def __str__(self):
        return f"{self.user.username} - {self.amount} UZS - {self.get_status_display()}"