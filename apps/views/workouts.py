from datetime import timedelta

from apps.models import Edition, Program
from apps.models.my_trainer import WorkoutSession
from apps.models.workouts import Workout, WorkoutExercise
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.aggregates import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
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


class WorkoutStartView(LoginRequiredMixin, View):
    template_name = 'workouts/active_workout.html'

    def get(self, request, pk):
        try:

            workout = get_object_or_404(Workout, pk=pk)

            workout_exercises = WorkoutExercise.objects.filter(
                workout=workout
            ).order_by('order').select_related('exercise')

            if not workout_exercises.exists():
                return render(request, 'eror_page.html', {'error_message': "Ushbu mashg'ulotda mashqlar mavjud emas."})

            exercises_data = []
            for wex in workout_exercises:

                is_strength = wex.sets > 0 or wex.reps > 0
                is_cardio = wex.minutes > 0

                if is_cardio and not is_strength:
                    exercise_type = 'cardio'
                else:
                    exercise_type = 'strength'

                exercise_thumbnail_url = wex.exercise.thumbnail.url if wex.exercise.thumbnail else None

                exercises_data.append({
                    'exercise_id': wex.exercise.id,
                    'name': wex.exercise.name,
                    'image': exercise_thumbnail_url,

                    'sets': wex.sets if wex.sets > 0 else 1,
                    'reps': wex.reps if wex.reps > 0 else 10,

                    'duration_minutes': wex.minutes,

                    'calories_per_minute': wex.exercise.calory if hasattr(wex.exercise,
                                                                          'calory') and wex.exercise.calory > 0 else 10,
                    'exercise_type': exercise_type,
                })

            context = {
                'workout': workout,
                'exercises': exercises_data,
                'total_exercises': len(exercises_data),
            }
            return render(request, self.template_name, context)

        except Exception as e:

            print(f"Server xatosi: {e}")
            return render(request, 'eror_page.html', {'error_message': f"Noma'lum xato yuz berdi: {str(e)}"})

    def post(self, request, pk):

        action = request.POST.get('action')

        if action == 'complete':

            return redirect('program_list')

        elif action == 'exit':
            save_progress = request.POST.get('save_progress') == 'true'

            if save_progress:
                pass

            return redirect('program_list')

        return redirect('workout_detail', pk=pk)


class WorkoutCompleteView(LoginRequiredMixin, View):

    def post(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)

        summary = request.session.get('workout_summary', {})

        if 'workout_summary' in request.session:
            del request.session['workout_summary']
            request.session.modified = True

        return render(request, "workouts/workout_complete.html", {
            "workout": workout,
            "summary": summary
        })

    def get(self, request, pk):
        workout = get_object_or_404(Workout, pk=pk)
        summary = request.session.get('workout_summary', {})

        if 'workout_summary' in request.session:
            del request.session['workout_summary']
            request.session.modified = True

        return render(request, "workouts/workout_complete.html", {
            "workout": workout,
            "summary": summary
        })


class MyTrainerView(LoginRequiredMixin, TemplateView):
    template_name = 'my_trainer/my_trainer.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

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
        user = self.request.user

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
                user=self.request.user
            )

            context['session'] = session
            context['exercise_logs'] = session.exercise_logs.all()

        except WorkoutSession.DoesNotExist:
            context['error'] = 'Workout session not found'

        return context
