from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    Model,
)


class Program(Model):
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
    edition = ForeignKey(Edition, on_delete=CASCADE, related_name='workouts')
    title = CharField(max_length=200)
    day_number = CharField(help_text="Edition ichida nechanchi kun")
    order = CharField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['edition', 'day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.title}"




