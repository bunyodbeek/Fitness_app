from apps.models import Favorite
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View


class FavoritesView(LoginRequiredMixin, TemplateView):
    template_name = 'exercises/favorites_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        favorite = Favorite.objects.filter(
            user=self.request.user.profile,
        ).order_by('-created_at')

        favorites_list = []
        for fav in favorite:

            obj = fav.exercise

            if obj:
                muscle_group_name = str(obj.primary_body_part)

                favorites_list.append({
                    'id': fav.id,
                    'title': obj.name,
                    'thumbnail_url': obj.thumbnail.url if obj.thumbnail else '',
                    'primary_body_part': muscle_group_name,
                    'difficulty': getattr(obj, 'difficulty', ''),
                    'equipment': getattr(obj, 'equipment', ''),

                    'exercise_id': fav.exercise_id,
                })

        context['favorites'] = favorites_list
        context['total_count'] = len(favorites_list)

        return context


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
