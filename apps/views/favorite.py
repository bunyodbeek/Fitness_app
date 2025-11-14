# views/favorites.py - YANGI FAYL

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from apps.models import Favorite


class FavoritesView(LoginRequiredMixin, TemplateView):
    """Barcha sevimlilar sahifasi"""
    template_name = 'exercises/favorites_list.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        favorite = Favorite.objects.filter(
            user=self.request.user.profile,
        ).order_by('-created_at')

        favorites_list = []
        for fav in favorite:
            obj = fav.content_object
            if obj:  # Check if object exists
                favorites_list.append({
                    'id': fav.id,
                    'title': obj.name if hasattr(obj, 'name') else getattr(obj, 'title', ''),
                    'thumbnail_url': obj.thumbnail.url if hasattr(obj, 'thumbnail') and obj.thumbnail else '',
                    'muscle_group': obj.muscle_group.name if hasattr(obj, 'muscle_group') else '',
                    'difficulty': getattr(obj, 'difficulty', ''),
                    'equipment': getattr(obj, 'equipment', ''),
                    'object_id': fav.object_id,
                })

        context['favorites'] = favorites_list
        context['total_count'] = len(favorites_list)

        return context


class ToggleFavoriteView(LoginRequiredMixin, View):
    """Favorite qo'shish/o'chirish - AJAX"""

    def post(self, request, content_type, object_id):
        try:
            # Get content type
            ct = ContentType.objects.get(model=content_type.lower())

            # Toggle favorite
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                content_type=ct,
                object_id=object_id
            )

            if not created:
                # Already exists - remove it
                favorite.delete()
                return JsonResponse({
                    'success': True,
                    'action': 'removed',
                    'is_favorite': False,
                    'message': 'Sevimlidan o\'chirildi'
                })
            else:
                # Just created
                return JsonResponse({
                    'success': True,
                    'action': 'added',
                    'is_favorite': True,
                    'message': 'Sevimliga qo\'shildi'
                })

        except ContentType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Noto\'g\'ri content type'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


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
