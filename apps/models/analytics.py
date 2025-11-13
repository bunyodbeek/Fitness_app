from django.db.models import CASCADE, CharField, DateTimeField, ForeignKey, JSONField, Model


class UserActivity(Model):
    EVENT_CHOICES = [
        ('bot_start', 'Bot Started'),
        ('onboarding_started', 'Onboarding Started'),
        ('onboarding_completed', 'Onboarding Completed'),
        ('subscription_page_viewed', 'Subscription Page Viewed'),
        ('payment_initiated', 'Payment Initiated'),
        ('payment_completed', 'Payment Completed'),
        ('program_viewed', 'Program Viewed'),
        ('workout_started', 'Workout Started'),
        ('workout_completed', 'Workout Completed'),
        ('exercise_viewed', 'Exercise Viewed'),
        ('exercise_favourited', 'Exercise Favourited'),
    ]

    user = ForeignKey('apps.UserProfile', CASCADE, related_name='activities')
    event = CharField(max_length=50, choices=EVENT_CHOICES)

    # Additional data
    metadata = JSONField(default=dict, blank=True)

    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Foydalanuvchi faoliyati'
        verbose_name_plural = 'Foydalanuvchi faoliyatlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.telegram_id} - {self.get_event_display()}"
