# apps/models/workout_session.py

from django.db import models
from django.contrib.auth import get_user_model
from apps.models.workouts import Workout

User = get_user_model()


class WorkoutSession(models.Model):

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('abandoned', 'Abandoned')
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_sessions'
    )
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )

    # Workout metrics
    duration_seconds = models.IntegerField(default=0)
    exercises_completed = models.IntegerField(default=0)
    total_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_reps = models.IntegerField(default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Current progress (for in-progress workouts)
    current_exercise_index = models.IntegerField(default=0)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Workout Session'
        verbose_name_plural = 'Workout Sessions'
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.workout.name} ({self.status})"

    @property
    def duration_minutes(self):
        """Duration in minutes"""
        return round(self.duration_seconds / 60, 1)

    @property
    def duration_formatted(self):
        """Formatted duration (H:MM)"""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}:{minutes:02d}"
        return f"{minutes}:00"


class ExerciseLog(models.Model):
    """Individual exercise log within a workout session"""

    session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name='exercise_logs'
    )
    exercise = models.ForeignKey(
        'Exercise',  # Your Exercise model
        on_delete=models.CASCADE
    )

    # Exercise data
    sets_completed = models.IntegerField(default=0)
    reps_completed = models.IntegerField(default=0)
    weight_used = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_seconds = models.IntegerField(default=0)
    calories_burned = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['started_at']
        verbose_name = 'Exercise Log'
        verbose_name_plural = 'Exercise Logs'

    def __str__(self):
        return f"{self.session.user.username} - {self.exercise.name}"