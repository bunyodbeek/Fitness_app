from django.db.models import Model, CharField, ForeignKey, FloatField, ImageField, BooleanField, DateTimeField, CASCADE, \
    TextChoices


class Program(Model):
    """Asosiy dastur - 'Get In Shape'"""
    title = CharField(max_length=200)
    description = CharField()
    image = ImageField(upload_to='programs/')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Edition(Model):
    """Dastur ichidagi variantlar - 'Machine focus', 'Adding dumbbells'"""
    program = ForeignKey(Program, on_delete=CASCADE, related_name='editions')
    title = CharField(max_length=200)
    order = CharField(default=0)
    duration_weeks = CharField(help_text="Dastur davomiyligi (haftalarda)")
    days_per_week = CharField(default=3, help_text="Haftasiga necha kun")
    description = CharField()
    image = ImageField(upload_to='editions/', null=True, blank=True)
    color = CharField(max_length=7, default='#FF6B35', help_text="Kartochka rangi (hex)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.program.title} - {self.title}"


class Workout(Model):
    """Bitta workout kunlik mashg'ulot"""
    edition = ForeignKey(Edition, on_delete=CASCADE, related_name='workouts')
    title = CharField(max_length=200)
    day_number = CharField(help_text="Edition ichida nechanchi kun")
    order = CharField(default=0)
    class Meta:
        ordering = ['order']
        unique_together = ['edition', 'day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"

    def total_exercises(self):
        return self.workout_exercises.count()


class WorkoutExercise(Model):
    """Workout ichidagi exercise"""

    class DurationType(TextChoices):
        REPS = 'reps', 'Reps'
        TIME = 'time', 'Time'

    DURATION_TYPE_CHOICES = [
        ('reps', 'Reps'),
        ('time', 'Time'),
    ]

    workout = ForeignKey(Workout, on_delete=CASCADE, related_name='workout_exercises')
    exercise = ForeignKey('apps.Exercise', on_delete=CASCADE)
    order = CharField(default=0)

    # Exercise parametrlari
    sets = CharField(default=3)
    reps = CharField(default=12, null=True, blank=True)
    duration_seconds = CharField(null=True, blank=True, help_text="Cardio uchun (sekundlarda)")
    duration_type = CharField(max_length=10, choices=DurationType.choices, default=DurationType.REPS)

    recommended_weight = FloatField(null=True, blank=True, help_text="Tavsiya etiladigan og'irlik (kg)")
    rest_seconds = CharField(default=60, help_text="Dam olish vaqti (sekundlarda)")

    notes = CharField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.duration_type == 'time':
            return f"{self.exercise.name} - {self.duration_seconds}s"
        return f"{self.exercise.name} - {self.sets}x{self.reps}"
