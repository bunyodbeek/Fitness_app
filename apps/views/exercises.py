from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.http import JsonResponse
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
    """
    URL'dan kelgan muscle_group nomiga asoslanib mashqlarni ro'yxatlaydi.
    Har bir mashq uchun foydalanuvchining sevimli holatini tekshiradi.
    """
    model = Exercise
    template_name = 'exercises/exercise_list.html'
    context_object_name = 'exercises'

    def get_queryset(self):
        """
        URL'dan kelgan 'muscle' nomiga ko'ra Mashq (Exercise) obyektlarini filtrlaydi.
        """

        muscle_name = self.kwargs['muscle']

        queryset = Exercise.objects.filter(
            muscle_group__iexact=muscle_name
        ).order_by('name')

        self.muscle = muscle_name

        return queryset

    def get_context_data(self, **kwargs):
        """
        Template'ga qo'shimcha kontekst ma'lumotlarini (muscle nomi va is_favorited) uzatadi.
        """
        context = super().get_context_data(**kwargs)

        context['muscle'] = self.muscle.capitalize()

        user = self.request.user

        if user.is_authenticated:

            try:
                user_profile = user.profile
            except AttributeError:
                user_profile = None

            if user_profile:
                exercise_ids = [exercise.id for exercise in context['exercises']]

                favorite_ids = Favorite.objects.filter(
                    user=user_profile,
                    exercise_id__in=exercise_ids
                ).values_list('exercise_id', flat=True)

                for exercise in context['exercises']:
                    exercise.is_favorited = exercise.id in favorite_ids
            else:
                for exercise in context['exercises']:
                    exercise.is_favorited = False
        else:

            for exercise in context['exercises']:
                exercise.is_favorited = False

        return context


class ExerciseDetailView(DetailView):
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
        if user.is_authenticated:

            try:
                user_profile = user.profile
            except AttributeError:
                user_profile = None

            if user_profile:
                context['is_favorited'] = Favorite.objects.filter(
                    user=user_profile,
                    exercise=self.object
                ).exists()
            else:
                context['is_favorited'] = False
        else:
            context['is_favorited'] = False

        return context


class ToggleFavoriteView(LoginRequiredMixin, View):

    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        user = request.user

        try:
            user_profile = user.profile
        except AttributeError:
            return JsonResponse({
                'success': False,
                'status': 'error',
                'message': 'Foydalanuvchida Profile obyekti topilmadi (user.profile chaqiruvi xato).'
            }, status=500)

        try:

            favorite_instance = Favorite.objects.get(user=user_profile, exercise=exercise)

            favorite_instance.delete()
            return JsonResponse({
                'success': True,
                'status': 'removed',
                'message': f"{exercise.name} sevimlilardan olib tashlandi."
            })

        except Favorite.DoesNotExist:

            try:

                Favorite.objects.create(user=user_profile, exercise=exercise)
                return JsonResponse({
                    'success': True,
                    'status': 'added',
                    'message': f"{exercise.name} sevimlilarga qo'shildi."
                })
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'status': 'error',
                    'message': 'Obekt allaqachon mavjud.'
                }, status=400)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'status': 'error',
                'message': str(e)
            }, status=500)


class AllExercisesView(ListView):
    model = Exercise
    template_name = 'exercises/all_exercises.html'
    context_object_name = 'exercises'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        muscle_filter = self.request.GET.get('muscle', '')
        if muscle_filter:
            queryset = queryset.filter(muscle_group_id=muscle_filter)

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

        context['difficulty_choices'] = Exercise.Difficulty.choices

        if self.request.user.is_authenticated:

            try:
                user_profile = self.request.user.profile
            except AttributeError:
                user_profile = None

            if user_profile:

                exercise_ct = ContentType.objects.get_for_model(Exercise)
                exercise_ids = self.object_list.values_list('id', flat=True)

                favorited = Favorite.objects.filter(

                    user=user_profile,
                    content_type=exercise_ct,
                    object_id__in=exercise_ids
                ).values_list('object_id', flat=True)

                context['favorited_ids'] = list(favorited)
            else:
                context['favorited_ids'] = []
        else:
            context['favorited_ids'] = []

        return context
