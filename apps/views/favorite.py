import json

from django.http import JsonResponse
from django.views import View
from rest_framework import status

from apps.models import Exercise, Favorite
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models.exercises import MuscleGroup
from apps.models.favorites import FavoriteCollection


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


class ToggleFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, exercise_id):
        exercise = get_object_or_404(Exercise, pk=exercise_id)
        user_profile = request.user.profile

        favorite, created = Favorite.objects.get_or_create(
            user=user_profile,
            exercise=exercise
        )

        if not created:
            favorite.delete()
            return Response({'success': True, 'status': 'removed'})

        return Response({'success': True, 'status': 'added'})

class FavoriteToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, collection_id):
        exercise_id = request.data.get('exercise_id')
        if not exercise_id:
            return Response(
                {"status": "error", "message": "Mashq ID si taqdim etilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        exercise = get_object_or_404(Exercise, id=exercise_id)
        collection = get_object_or_404(FavoriteCollection, id=collection_id, user=request.user)

        favorite = Favorite.objects.filter(user=request.user, exercise=exercise, collection=collection).first()
        if favorite:
            favorite.delete()
            action = 'removed'
            message = f'"{exercise.name}" mashqi "{collection.name}" toʻplamidan olib tashlandi.'
        else:
            Favorite.objects.create(user=request.user, exercise=exercise, collection=collection)
            action = 'added'
            message = f'"{exercise.name}" mashqi "{collection.name}" toʻplamiga qoʻshildi.'

        return Response({
            "status": "success",
            "action": action,
            "exercise_id": exercise.id,
            "collection_id": collection.id,
            "message": message,
            "items_count": collection.items_count
        }, status=status.HTTP_200_OK)


class AddExerciseToCollectionView(LoginRequiredMixin, View):
    """
    POST orqali mashqni belgilangan FavoriteCollection-ga qo'shadi.
    """
    def post(self, request, collection_id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            exercise_id = data.get('exercise_id')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Yaroqsiz JSON.'}, status=400)

        if not exercise_id:
            return JsonResponse({'success': False, 'error': 'Mashq ID taqdim etilmadi.'}, status=400)

        # Mashq va to'plamni olish
        exercise = get_object_or_404(Exercise, id=exercise_id)
        collection = get_object_or_404(FavoriteCollection, id=collection_id, user=request.user.profile)

        # Agar mashq allaqachon to'plamda bo'lsa
        if collection.favorites.filter(exercise=exercise).exists():
            return JsonResponse({'success': False, 'error': 'Mashq allaqachon to‘plamda mavjud.'})

        # Mashqni to'plamga qo'shish
        collection.favorites.create(user=request.user.profile, exercise=exercise)

        return JsonResponse({'success': True, 'message': f'"{exercise.name}" mashqi "{collection.name}" to‘plamga qo‘shildi.'})



class CreateCollectionVIew(CreateView):

    def get(self, request, *args, **kwargs):
        create_collection = request.GET.get("create_collection")
        exercise_id = request.GET.get("exercise_id")

        if create_collection == "true" and exercise_id:
            context = self.get_context_data(exercise_id=exercise_id)
            return self.render_to_response(context)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercise_id = kwargs.get("exercise_id")
        context["exercise_id"] = exercise_id
        context["user_collections"] = self.request.user.profile.favorite_collections.all()
        return context