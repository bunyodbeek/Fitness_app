from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import CreateView, ListView
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models import Exercise, Favorite
from apps.models.favorites import FavoriteCollection


class FavoritesListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'exercises/favorites_list.html'
    context_object_name = 'favorites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile
        context['total_count'] = Favorite.objects.filter(user=user_profile).count()
        context['favorite_collections'] = FavoriteCollection.objects.filter(user=user_profile).order_by('-created_at')
        context['collections_count'] = context['favorite_collections'].count()
        context['all_exercises'] = [fav.exercise for fav in self.get_queryset()]
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        qs = qs.filter(user=user.profile, collection__isnull=True).select_related('exercise')
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


class FavoriteToggleAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, collection_id):
        exercise_id = request.data.get("exercise_id")
        if not exercise_id:
            return Response(
                {"message": "Mashq ID si yuborilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user.profile
        collection = get_object_or_404(FavoriteCollection, id=collection_id, user=user)
        exercise = get_object_or_404(Exercise, id=exercise_id)

        qs = Favorite.objects.filter(user=user, collection=collection, exercise=exercise)

        if qs.exists():
            qs.delete()
            action = "removed"
            message = f'"{exercise.name}" mashqi "{collection.name}" toʻplamidan olib tashlandi.'
        else:
            obj, created = Favorite.objects.get_or_create(user=user, exercise=exercise)
            obj.collection = collection
            obj.save(update_fields=['collection'])

            action = "added"
            message = f'"{exercise.name}" mashqi "{collection.name}" toʻplamiga qoʻshildi.'

        return Response({
            "success": True,
            "action": action,
            "exercise_id": exercise.id,
            "collection_id": collection.id,
            "items_count": collection.exercise_count,
            "message": message,
        })


class CreateCollectionView(View):
    @transaction.atomic
    def post(self, request):
        name = request.POST.get("name")
        exercise_id = request.POST.get("exercise_id")
        exercise_ids = request.POST.getlist("exercise_ids[]")

        if not name:
            return JsonResponse(
                {"success": False, "error": "Collection nomi yuborilmadi"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user.profile

        collection = FavoriteCollection.objects.create(
            user=user,
            name=name
        )

        all_exercise_ids = []

        if exercise_id:
            all_exercise_ids.append(int(exercise_id))

        for ex_id in exercise_ids:
            all_exercise_ids.append(int(ex_id))

        for ex_id in set(all_exercise_ids):
            exercise = get_object_or_404(Exercise, id=ex_id)

            favorite, created = Favorite.objects.get_or_create(
                user=user,
                exercise=exercise,
                defaults={"collection": collection}
            )

            if not created and favorite.collection is None:
                favorite.collection = collection
                favorite.save(update_fields=["collection"])

        return JsonResponse({
            "success": True,
            "collection_id": collection.id,
            "name": collection.name
        }, status=status.HTTP_201_CREATED)
