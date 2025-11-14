# views/favorites.py - YANGI FAYL

from apps.models import Favorite
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View


# apps/views/favorite.py

# ... boshqa importlar (Favorite modelini import qilish shart)

class FavoritesView(LoginRequiredMixin, TemplateView):
    """Barcha sevimlilar sahifasi"""
    template_name = 'exercises/favorites_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Profile obyekti orqali Sevimlilarni filtrlaymiz (To'g'ri)
        favorite = Favorite.objects.filter(
            user=self.request.user.profile,
        ).order_by('-created_at')

        favorites_list = []
        for fav in favorite:
            # ⭐ ASOSIY TUZATISH 1: fav.content_object o'rniga fav.exercise ishlatiladi
            obj = fav.exercise

            if obj:  # Check if Exercise object exists
                # 2. obj.muscle_group to'g'ridan-to'g'ri CharField deb faraz qilamiz
                muscle_group_name = str(obj.muscle_group)

                favorites_list.append({
                    'id': fav.id,
                    'title': obj.name,
                    'thumbnail_url': obj.thumbnail.url if obj.thumbnail else '',
                    'muscle_group': muscle_group_name,
                    'difficulty': getattr(obj, 'difficulty', ''),
                    'equipment': getattr(obj, 'equipment', ''),
                    # 3. Object ID o'rniga exercise ID ni yuboramiz
                    'exercise_id': fav.exercise_id,
                })

        context['favorites'] = favorites_list
        context['total_count'] = len(favorites_list)

        return context
# ... qolgan View'lar (ToggleFavoriteView va RemoveFavoriteView)


class RemoveFavoriteView(LoginRequiredMixin, View):
    """Favorite o'chirish"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def delete(self, request, favorite_id):
        try:
            favorite = Favorite.objects.get(
                id=favorite_id,
                user=request.user
            )
            favorite.delete()

            return JsonResponse({
                'success': True,
                'message': 'Sevimlidan o\'chirildi'
            })
        except Favorite.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Sevimli topilmadi'
            }, status=404)

    def post(self, request, favorite_id):
        """POST method ham qo'llab-quvvatlash"""
        return self.delete(request, favorite_id)
