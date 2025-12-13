from datetime import timedelta

from apps.models import Edition, Program
from apps.models.my_trainer import WorkoutProgress, WorkoutSession
from apps.models.workouts import Workout, WorkoutExercise
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.aggregates import Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView


class AnimationView(TemplateView):
    template_name = 'animation.html'


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

    def get(self, request, *args, **kwargs):
        if not request.user.profile.is_premium:
            return redirect('premium_page')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        workout_pks = Workout.objects.filter(edition=self.object).values_list('pk', flat=True)

        workout_exercises = WorkoutExercise.objects.filter(
            workout__in=workout_pks
        ).select_related('exercise')

        context['workouts'] = workout_exercises

        context['total_exercises'] = workout_exercises.count()

        return context


class WorkoutStartView(LoginRequiredMixin, View):
    template_name = 'workouts/active_workout.html'

    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        workout_exercises = (
            WorkoutExercise.objects
            .filter(workout=workout)
            .select_related('exercise')
            .order_by('order')
        )

        if not workout_exercises.exists():
            return render(request, 'error_page.html', {
                "error_message": "Ushbu workoutda mashqlar mavjud emas."
            })

        exercises_data = self._prepare_exercises_data(workout_exercises)

        return render(request, self.template_name, {
            "workout": workout,
            "exercises": exercises_data,
            "total_exercises": len(exercises_data)
        })

    def post(self, request, pk):
        action = request.POST.get("action")
        save = request.POST.get("save_progress") == "true"

        workout = get_object_or_404(Workout, pk=pk)

        # Workout finished
        if action == "complete":
            WorkoutProgress.objects.update_or_create(
                user=request.user.profile,
                workout=workout,
                defaults={
                    "total_duration_seconds": int(request.POST.get("total_duration", 0)),
                    "total_calories": float(request.POST.get("total_calories", 0)),
                    "exercises_completed": int(request.POST.get("exercises_completed", 0)),
                }
            )
            return redirect("workout_complete", pk)

        # Exit with save
        if action == "exit" and save:
            WorkoutProgress.objects.update_or_create(
                user=request.user.profile,
                workout=workout,
                defaults={
                    "total_duration_seconds": int(request.POST.get("total_duration", 0)),
                    "total_calories": float(request.POST.get("total_calories", 0)),
                    "exercises_completed": int(request.POST.get("exercises_completed", 0)),
                }
            )
            return redirect("program_list")

        if action == "exit" and not save:
            return redirect("program_list")

        return HttpResponseBadRequest("Invalid request")

    def _prepare_exercises_data(self, workout_exercises):
        data = []
        for wex in workout_exercises:
            exercise = wex.exercise

            is_strength = wex.sets > 0 or wex.reps > 0
            is_cardio = wex.minutes > 0
            exercise_type = "cardio" if is_cardio and not is_strength else "strength"

            data.append({
                "exercise_id": exercise.id,
                "name": exercise.name,
                "image": exercise.thumbnail.url if exercise.thumbnail else None,
                "sets": max(wex.sets, 1),
                "reps": max(wex.reps, 10),
                "duration_minutes": wex.minutes,
                "rest_seconds": getattr(wex, 'rest_seconds', 60),
                "calories_per_minute": max(exercise.calory, 10),
                "type": exercise_type,
            })
        return data


class WorkoutCompleteView(LoginRequiredMixin, View):
    template_name = "workouts/workout_complete.html"

    def post(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)

        try:
            total_calories = float(request.POST.get("total_calories", 0))
            total_duration = int(request.POST.get("total_duration", 0))
            exercises_completed = int(request.POST.get("exercises_completed", 0))
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid input data")

        WorkoutProgress.objects.create(
            user=request.user.profile,
            workout=workout,
            total_calories=total_calories,
            total_duration_seconds=total_duration,
            exercises_completed=exercises_completed
        )

        return render(request, self.template_name, {
            "workout": workout,
            "workout_summary": {
                "total_calories": total_calories,
                "duration_seconds": total_duration,
                "exercises_completed": exercises_completed,
                "total_reps": 0,
                "total_weight": 0
            }
        })

    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        return render(request, self.template_name, {"workout": workout})


class MyTrainerView(LoginRequiredMixin, TemplateView):
    template_name = 'my_trainer/my_trainer.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.profile

        sessions = WorkoutSession.objects.filter(user=user)
        completed_sessions = sessions.filter(status='completed')

        total_workouts = completed_sessions.count()

        total_duration = completed_sessions.aggregate(
            total=Sum('duration_seconds')
        )['total'] or 0

        total_calories = completed_sessions.aggregate(
            total=Sum('total_calories')
        )['total'] or 0

        current_streak = self.calculate_streak(user)

        context['user_stats'] = {
            'total_workouts': total_workouts,
            'total_duration_hours': round(total_duration / 3600, 1),
            'total_calories': int(total_calories),
            'current_streak': current_streak
        }

        recent_workouts = sessions.select_related('workout', 'workout__edition').order_by('-started_at')[:10]

        context['recent_workouts'] = recent_workouts

        return context

    def calculate_streak(self, user):

        today = timezone.now().date()
        streak = 0
        current_date = today

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

                if current_date != today:
                    break
                current_date -= timedelta(days=1)

        return streak


class MyTrainerHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'my_trainer/my_trainer_history.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.profile

        all_sessions = WorkoutSession.objects.filter(
            user=user
        ).select_related('workout', 'workout__edition').order_by('-started_at')

        context['all_workouts'] = all_sessions

        return context


class WorkoutDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'my_trainer/workouts_detail.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_id = kwargs.get('session_id')

        try:
            session = WorkoutSession.objects.select_related(
                'workout', 'workout__edition'
            ).prefetch_related('exercise_logs__exercise').get(
                id=session_id,
                user=self.request.user.profile
            )

            context['session'] = session
            context['exercise_logs'] = session.exercise_logs.all()

        except WorkoutSession.DoesNotExist:
            context['error'] = 'Workout session not found'

        return context
