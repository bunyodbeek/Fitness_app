from apps.models import Edition, Program, Workout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView


class ProgramListView(ListView):
    queryset = Program.objects.filter(is_active=True).prefetch_related('editions')
    template_name = 'workouts/program_list.html'
    context_object_name = 'programs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agar user login qilgan bo'lsa, uning favourite dasturlarini olamiz
        if self.request.user.is_authenticated:
            # Bu keyinroq my_trainer appdan keladi
            context['user_favorites'] = []
        return context


class ProgramDetailView(DetailView):
    """Dastur detali - EDITIONS sahifasi"""
    model = Program
    template_name = 'workouts/program_detail.html'
    context_object_name = 'program'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editions'] = self.object.editions.all()
        return context


class EditionDetailView(DetailView):
    """Edition detali - Workoutlar ro'yxati"""
    model = Edition
    template_name = 'workouts/edition_detail.html'
    context_object_name = 'edition'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['workouts'] = self.object.workouts.prefetch_related(
            'workout_exercises__exercise'
        ).all()
        return context


class WorkoutDetailView(DetailView):
    """Workout detali - Exercise list ko'rish"""
    model = Workout
    template_name = 'workouts/workout_detail.html'
    context_object_name = 'workout'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercises'] = self.object.workout_exercises.select_related(
            'exercise'
        ).all()
        return context


class WorkoutStartView(LoginRequiredMixin, DetailView):
    """Workout boshlash - Active session"""
    model = Workout
    template_name = 'workouts/workout_start.html'
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
        """Workout yakunlanganda - my_trainer appga save qilish"""
        # Bu keyinroq my_trainer app bilan integrate qilamiz
        workout = self.get_object()

        # Workout ma'lumotlarini olish
        workout_data = {
            'duration': request.POST.get('duration'),
            'completed_exercises': request.POST.get('completed_exercises'),
            'total_reps': request.POST.get('total_reps'),
            'total_weight': request.POST.get('total_weight'),
        }

        # Keyinroq bu yerda my_trainer appga save qilamiz
        # CompletedWorkout.objects.create(...)

        return redirect('workouts:workout_complete', workout_id=workout.id)


class WorkoutCompleteView(LoginRequiredMixin, DetailView):
    """Workout tugallangandan keyin - Summary sahifasi"""
    model = Workout
    template_name = 'workouts/workout_complete.html'
    context_object_name = 'workout'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Keyinroq bu ma'lumotlarni my_trainer appdan olamiz
        context['summary'] = {
            'total_reps': 0,
            'total_weight': 0,
            'duration': '0:00',
        }
        return context
