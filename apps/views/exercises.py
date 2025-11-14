from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView, ListView

from apps.models import Exercise, Favorite
from apps.models.exercises import MuscleGroup


class MuscleGroupListView(View):
    template_name = 'exercises/body_parts.html'
    context_object_name = 'body_parts'

    def get(self, request):
        muscle_groups = [
            {"value": choice.value, "label": choice.label}
            for choice in MuscleGroup
        ]
        context = {"muscle_groups": muscle_groups}
        return render(request, self.template_name, context)


class ExercisesByMuscleView(ListView):
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'

    def get_queryset(self):
        muscle_id = self.kwargs.get('muscle_id')
        muscle_group = get_object_or_404(MuscleGroup, id=muscle_id)
        return muscle_group.exercises.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        muscle_id = self.kwargs.get('muscle_id')
        context['muscle_group'] = get_object_or_404(MuscleGroup, id=muscle_id)

        if self.request.user.is_authenticated:
            exercise_ct = ContentType.objects.get_for_model(Exercise)
            exercise_ids = self.object_list.values_list('id', flat=True)

            favorited = Favorite.objects.filter(
                user=self.request.user,
                content_type=exercise_ct,
                object_id__in=exercise_ids
            ).values_list('object_id', flat=True)

            context['favorited_ids'] = list(favorited)
        else:
            context['favorited_ids'] = []

        return context


class ExerciseDetailView(DetailView):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'
    pk_url_kwarg = 'exercise_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instructions'] = self.object.instructions.all()

        # Is this favorited?
        if self.request.user.is_authenticated:
            exercise_ct = ContentType.objects.get_for_model(Exercise)
            context['is_favorited'] = Favorite.objects.filter(
                user=self.request.user,
                content_type=exercise_ct,
                object_id=self.object.id
            ).exists()
        else:
            context['is_favorited'] = False

        return context


class AllExercisesView(ListView):
    """Barcha mashqlar - filter bilan"""
    model = Exercise
    template_name = 'exercises/all_exercises.html'
    context_object_name = 'exercises'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Qidiruv
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        # Mushak guruhi bo'yicha filter
        muscle_filter = self.request.GET.get('muscle', '')
        if muscle_filter:
            queryset = queryset.filter(muscle_group_id=muscle_filter)

        # Qiyinlik darajasi bo'yicha filter
        difficulty_filter = self.request.GET.get('difficulty', '')
        if difficulty_filter:
            queryset = queryset.filter(difficulty=difficulty_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['muscle_groups'] = MuscleGroup.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_muscle'] = self.request.GET.get('muscle', '')
        context['selected_difficulty'] = self.request.GET.get('difficulty', '')

        # Difficulty choices
        context['difficulty_choices'] = Exercise.Difficulty.choices

        # Favorited IDs
        if self.request.user.is_authenticated:
            exercise_ct = ContentType.objects.get_for_model(Exercise)
            exercise_ids = self.object_list.values_list('id', flat=True)

            favorited = Favorite.objects.filter(
                user=self.request.user,
                content_type=exercise_ct,
                object_id__in=exercise_ids
            ).values_list('object_id', flat=True)

            context['favorited_ids'] = list(favorited)
        else:
            context['favorited_ids'] = []

        return context
