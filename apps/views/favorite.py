from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Exercise, Favorite


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
            qs = qs.filter(user=self.request.user.profile)
        return qs


class ToggleFavoriteView(LoginRequiredMixin, APIView):
    login_url = '/login/'

    def post(self, request, exercise_id):
        return self.toggle_favorite(request, exercise_id)

    def delete(self, request, exercise_id):
        return self.toggle_favorite(request, exercise_id)

    def toggle_favorite(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        user_profile = getattr(request.user, "profile", None)
        if not user_profile:
            return Response({'success': False, 'message': 'Profile topilmadi.'}, status=500)

        favorite_instance, created = Favorite.objects.get_or_create(
            user=user_profile,
            exercise=exercise
        )
        if created:
            status = 'added'
        else:
            favorite_instance.delete()
            status = 'removed'

        return Response({'success': True, 'status': status})

#
# class RemoveFavoriteView(LoginRequiredMixin, View):
#     @method_decorator(csrf_exempt)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
#
#     def delete(self, request, favorite_id):
#
#         try:
#
#             user_profile = request.user.profile
#         except AttributeError:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Foydalanuvchi tizimga kirmagan yoki Profile obyekti mavjud emas.'
#             }, status=400)
#
#         try:
#             favorite = Favorite.objects.get(
#                 id=favorite_id,
#                 user=user_profile
#             )
#             favorite.delete()
#
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Sevimlidan muvaffaqiyatli o\'chirildi'
#             })
#         except Favorite.DoesNotExist:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Sevimli ro\'yxatda topilmadi.'
#             }, status=404)
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': f'Kutilmagan xato: {str(e)}'
#             }, status=500)
#
#     def post(self, request, favorite_id):
#         return self.delete(request, favorite_id)
