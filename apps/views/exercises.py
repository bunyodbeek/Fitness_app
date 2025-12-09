from apps.models import Exercise, Favorite
from apps.models.exercises import MuscleGroup
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView


class MuscleGroupListView(TemplateView):
    template_name = 'exercises/body_parts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["body_parts"] = [
            {"value": choice.value, "label": choice.label}
            for choice in MuscleGroup
        ]
        return context


class ExercisesByMuscleView(ListView):
    queryset = Exercise.objects.order_by('name')
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'

    def get_queryset(self):
        qs = super().get_queryset()
        muscle_name = self.kwargs['muscle']
        qs = qs.filter(primary_body_part__iexact=muscle_name)
        self.muscle = muscle_name
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['muscle'] = self.muscle.capitalize()
        user = self.request.user
        try:
            user_profile = user.profile
        except AttributeError:
            user_profile = None
        if user_profile:
            exercise_ids = [exercise.id for exercise in context['exercises']]
            favorite_ids = Favorite.objects.filter(user=user_profile, exercise_id__in=exercise_ids).values_list(
                'exercise_id', flat=True)
            for exercise in context['exercises']:
                exercise.is_favorited = exercise.id in favorite_ids
            context['user_collections'] = user_profile.favorite_collections.all()
        else:
            for exercise in context['exercises']:
                exercise.is_favorited = False
        return context


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    model = Exercise
    template_name = 'exercises/exercise_detail.html'
    context_object_name = 'exercise'
    pk_url_kwarg = 'exercise_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        final_instructions_list = []
        if hasattr(self.object, 'instructions'):
            for instruction_obj in self.object.instructions.all():
                instruction_text = getattr(instruction_obj, 'text', None)
                if instruction_text:
                    lines = [
                        line.strip()
                        for line in instruction_text.splitlines()
                        if line.strip()
                    ]
                    final_instructions_list.extend(lines)

        context['instructions_list'] = final_instructions_list
        user = self.request.user
        try:
            user_profile = user.profile
        except AttributeError:
            user_profile = None
        if user_profile:
            context['is_favorited'] = Favorite.objects.filter(user=user_profile, exercise=self.object).exists()
        else:
            context['is_favorited'] = False
        return context
