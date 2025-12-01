from django.db.models import CASCADE, ForeignKey, Index, Model, FloatField
from django.db.models.enums import TextChoices
from django.db.models.fields import CharField, DateTimeField, DecimalField, IntegerField


class WorkoutSession(Model):
    class StatusChoices(TextChoices):
        COMPLETED = 'completed', 'Completed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        ABANDONED = 'abandoned', 'Abandoned'

    user = ForeignKey('apps.User', CASCADE, related_name='workout_sessions')
    workout = ForeignKey('apps.Workout', CASCADE, related_name='sessions')
    status = CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.IN_PROGRESS)

    duration_seconds = IntegerField(default=0)
    exercises_completed = IntegerField(default=0)
    total_calories = DecimalField(max_digits=8, decimal_places=2, default=0)
    total_reps = IntegerField(default=0)
    total_weight = DecimalField(max_digits=10, decimal_places=2, default=0)

    current_exercise_index = IntegerField(default=0)

    started_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True, blank=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Workout Session'
        verbose_name_plural = 'Workout Sessions'
        indexes = [
            Index(fields=['user', '-started_at']),
            Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.workout.title} ({self.status})"

    @property
    def duration_minutes(self):
        return round(self.duration_seconds / 60, 1)

    @property
    def duration_formatted(self):
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}:{minutes:02d}"
        return f"{minutes}:00"


class ExerciseLog(Model):
    session = ForeignKey('apps.WorkoutSession', CASCADE, related_name='exercise_logs')
    exercise = ForeignKey('Exercise', CASCADE)

    sets_completed = IntegerField(default=0)
    reps_completed = IntegerField(default=0)
    weight_used = DecimalField(max_digits=8, decimal_places=2, default=0)
    duration_seconds = IntegerField(default=0)
    calories_burned = DecimalField(max_digits=6, decimal_places=2, default=0)

    started_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['started_at']
        verbose_name = 'Exercise Log'
        verbose_name_plural = 'Exercise Logs'

    def __str__(self):
        return f"{self.session.user.username} - {self.exercise.name}"


class WorkoutProgress(Model):
    user = ForeignKey('apps.UserProfile', on_delete=CASCADE)
    workout = ForeignKey('Workout', on_delete=CASCADE)
    total_calories = FloatField(default=0)
    total_duration_seconds = IntegerField(default=0)
    exercises_completed = IntegerField(default=0)
    completed_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.workout} progress"
