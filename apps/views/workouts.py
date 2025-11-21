from apps.models import Edition, Program, Exercise
from apps.models.my_trainer import WorkoutSession
from apps.models.workouts import Workout, WorkoutExercise
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView


class AnimationView(TemplateView):
    template_name = 'workouts/animation.html'
class ProgramListView(ListView):
    queryset = Program.objects.filter(is_active=True).prefetch_related('editions')
    template_name = 'workouts/program_list.html'
    context_object_name = 'programs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        editions = Edition.objects.filter(program__in=self.object_list).prefetch_related('workouts__workout_exercises')

        workouts = Workout.objects.filter(edition__in=editions).prefetch_related("workout_exercises")

        total_days = workouts.values('day_number').distinct().count()

        context['workouts'] = workouts
        context['total_days'] = total_days

        if self.request.user.is_authenticated:
            context['user_favorites'] = []

        return context


class ProgramDetailView(DetailView):
    model = Program
    template_name = 'workouts/edition_list.html'
    context_object_name = 'program'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editions'] = self.object.editions.all()
        return context


class EditionDetailView(DetailView):
    model = Edition
    template_name = 'workouts/edition_detail.html'
    context_object_name = 'edition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        workout_pks = Workout.objects.filter(edition=self.object).values_list('pk', flat=True)

        workout_exercises = WorkoutExercise.objects.filter(
            workout__in=workout_pks
        ).select_related('exercise')

        context['workouts'] = workout_exercises

        context['total_exercises'] = workout_exercises.count()

        return context



class WorkoutStartView(LoginRequiredMixin, DetailView):
    model = Workout
    template_name = 'workouts/active_workout.html'
    context_object_name = 'workout'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercises = self.object.workout_exercises.select_related('exercise').all()

        context['exercises'] = exercises
        context['total_exercises'] = exercises.count()
        context['edition'] = self.object.edition

        return context

    def post(self, request, *args, **kwargs):
        workout = self.get_object()

        workout_data = {
            'duration': request.POST.get('duration'),
            'completed_exercises': request.POST.get('completed_exercises'),
            'total_reps': request.POST.get('total_reps'),
            'total_weight': request.POST.get('total_weight'),
        }

        return redirect('workout_complete', workout_id=workout.id, data=workout_data)


class WorkoutCompleteView(LoginRequiredMixin, DetailView):
    model = Workout
    template_name = 'workouts/workout_complete.html'
    context_object_name = 'workout'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Session dan summary ni olish
        summary = self.request.session.get('workout_summary', {})

        context['summary'] = {
            'total_reps': summary.get('total_reps', 0),
            'total_weight': summary.get('total_weight', 0),
            'duration': summary.get('duration', '0:00'),
        }

        # Summary ishlatilgandan keyin tozalash
        if 'workout_summary' in self.request.session:
            del self.request.session['workout_summary']
            self.request.session.modified = True

        return context


# apps/views/workouts.py

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime


class MyTrainerView(LoginRequiredMixin, TemplateView):
    """User's personal trainer dashboard"""

    template_name = 'my_trainer/my_trainer.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get all user's sessions
        sessions = WorkoutSession.objects.filter(user=user)
        completed_sessions = sessions.filter(status='completed')

        # Calculate statistics
        total_workouts = completed_sessions.count()

        total_duration = completed_sessions.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0

        total_calories = completed_sessions.aggregate(
            total=Sum('total_calories')
        )['total'] or 0

        # Calculate current streak
        current_streak = self.calculate_streak(user)

        context['user_stats'] = {
            'total_workouts': total_workouts,
            'total_duration_hours': round(total_duration / 3600, 1),
            'total_calories': int(total_calories),
            'current_streak': current_streak
        }

        # Get recent workouts (last 10)
        recent_workouts = sessions.select_related('workout', 'workout__edition').order_by('-started_at')[:10]

        context['recent_workouts'] = recent_workouts

        return context

    def calculate_streak(self, user):
        """Calculate consecutive days with completed workouts"""
        today = timezone.now().date()
        streak = 0
        current_date = today

        # Check up to 100 days back (reasonable limit)
        for _ in range(100):
            has_workout = WorkoutSession.objects.filter(
                user=user,
                started_at__date=current_date,
                status='completed'
            ).exists()

            if has_workout:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                # Break streak only if not today (user might not have worked out yet today)
                if current_date != today:
                    break
                current_date -= timedelta(days=1)

        return streak


class MyTrainerHistoryView(LoginRequiredMixin, TemplateView):
    """Full workout history"""

    template_name = 'my_trainer/my_trainer_history.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get all sessions
        all_sessions = WorkoutSession.objects.filter(
            user=user
        ).select_related('workout', 'workout__edition').order_by('-started_at')

        context['all_workouts'] = all_sessions

        return context


class WorkoutDetailView(LoginRequiredMixin, TemplateView):
    """Detailed view of a specific workout session"""

    template_name = 'my_trainer/workout_detail.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = kwargs.get('session_id')

        try:
            session = WorkoutSession.objects.select_related(
                'workout', 'workout__edition'
            ).prefetch_related('exercise_logs__exercise').get(
                id=session_id,
                user=self.request.user
            )

            context['session'] = session
            context['exercise_logs'] = session.exercise_logs.all()

        except WorkoutSession.DoesNotExist:
            context['error'] = 'Workout session not found'

        return context