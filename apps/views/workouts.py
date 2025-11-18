from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from apps.models import Edition, Program
from apps.models.workouts import EditionExercise, Workout


class ProgramListView(ListView):
    queryset = Program.objects.filter(is_active=True).prefetch_related('editions')
    template_name = 'workouts/program_list.html'
    context_object_name = 'programs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        workouts = self.object.edition_exercises.select_related('exercise').all()

        context['workouts'] = workouts
        context['total_exercises'] = workouts.count()

        return context



class WorkoutDetailView(DetailView):
    model = EditionExercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'workout'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercises'] = self.object.edition_exercises.select_related(
            'exercise'
        ).all()
        return context

class WorkoutStartView(LoginRequiredMixin, DetailView):
    model = Workout
    template_name = 'workouts/edition_detail.html'
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

        context['summary'] = {
            'total_reps': 0,
            'total_weight': 0,
            'duration': '0:00',
        }
        return context
