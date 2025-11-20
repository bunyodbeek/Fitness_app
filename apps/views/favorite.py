from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView, CreateView

from apps.models import Favorite, Exercise


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'exercises/favorites_list.html'
    login_url = '/login/'
    context_object_name = 'favorites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Favorite.objects.filter(user=self.request.user.profile).count()
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            qs.filter(user=self.request.user.profile)
        return qs



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


class RemoveFavoriteView(LoginRequiredMixin, View):
    """Favorite o'chirish"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, favorite_id):

        try:

            user_profile = request.user.profile
        except AttributeError:
            return JsonResponse({
                'success': False,
                'error': 'Foydalanuvchi tizimga kirmagan yoki Profile obyekti mavjud emas.'
            }, status=400)

        try:
            favorite = Favorite.objects.get(
                id=favorite_id,
                user=user_profile
            )
            favorite.delete()

            return JsonResponse({
                'success': True,
                'message': 'Sevimlidan muvaffaqiyatli o\'chirildi'
            })
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Sevimli ro\'yxatda topilmadi.'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Kutilmagan xato: {str(e)}'
            }, status=500)

    def post(self, request, favorite_id):
        return self.delete(request, favorite_id)
