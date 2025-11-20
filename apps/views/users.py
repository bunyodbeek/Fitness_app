import json
import traceback

import requests
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.forms import UserProfileForm
from apps.models import User, UserMotivation, UserProfile
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView


@method_decorator(csrf_exempt, name='dispatch')
class QuestionnaireSubmitView(View):

    def parse_json(self, request):

        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return None

    def get_or_update_user(self, telegram_id, first_name, last_name):

        user, created = User.objects.get_or_create(
            username=f"telegram_{telegram_id}",
            defaults={'first_name': first_name, 'last_name': last_name}
        )

        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        return user, created

    def create_or_update_profile(self, user, data):

        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'telegram_id': data['telegram_id'],
                'name': data['first_name']
            }
        )

        profile.telegram_id = data['telegram_id']
        profile.telegram_username = data.get('username', '')
        profile.name = data['first_name']
        profile.gender = data.get('gender', 'male')
        profile.experience_level = data.get('experience', 'beginner')
        profile.fitness_goal = data.get('goal', 'build_body')
        profile.workout_days_per_week = int(data.get('days', 3))
        profile.weight = float(data.get('weight', 63))
        profile.onboarding_completed = True

        self.save_avatar_if_exists(profile, data.get('photo_url'))
        profile.save()

        return profile

    def save_avatar_if_exists(self, profile, photo_url):

        if not photo_url:
            return

        try:
            response = requests.get(photo_url, timeout=5)
            if response.status_code == 200:
                profile.avatar.save(
                    f"{profile.telegram_id}.jpg",
                    ContentFile(response.content),
                    save=False
                )
        except Exception as e:
            print(f"Avatar save error: {e}")

    def save_motivations(self, profile, motivations):

        UserMotivation.objects.filter(user=profile).delete()
        for m in motivations:
            UserMotivation.objects.create(user=profile, motivation=m)

    def post(self, request, *args, **kwargs):
        data = self.parse_json(request)
        if data is None:
            return JsonResponse({'success': False, 'error': 'Noto‘g‘ri JSON format'}, status=400)

        telegram_id = data.get('telegram_id')
        if not telegram_id:
            return JsonResponse({'success': False, 'error': 'Telegram ID topilmadi'}, status=400)

        existing_profile = UserProfile.objects.filter(telegram_id=telegram_id).first()
        if existing_profile:
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('animation'),
                'message': 'User already exists'
            })

        try:

            user, is_new = self.get_or_update_user(
                telegram_id,
                data.get('first_name', 'User'),
                data.get('last_name', '')
            )

            profile = self.create_or_update_profile(user, data)

            self.save_motivations(profile, data.get('motivation', []))

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return JsonResponse({
                'success': True,
                'message': "Ma'lumotlar saqlandi",
                'redirect_url': reverse('animation'),
                'is_new_user': is_new,
                'user_id': user.id,
                'profile_id': profile.id,
                'telegram_id': telegram_id
            })

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramAuthView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            telegram_id = data.get('telegram_id')

            if not telegram_id:
                return JsonResponse({'success': False, 'error': 'Telegram ID not found'}, status=400)

            profile = UserProfile.objects.filter(telegram_id=telegram_id).first()

            if profile:
                user = profile.user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                if profile.onboarding_completed:
                    return JsonResponse({
                        'success': True,
                        'redirect': '/',
                        'onboarding_completed': True,
                        'user_id': user.id
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'redirect': '/miniapp/questionnaire/',
                        'onboarding_completed': False
                    })

            return JsonResponse({
                'success': True,
                'redirect': '/miniapp/questionnaire/',
                'onboarding_completed': False,
                'is_new_user': True
            })

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def get(self, request):
        return HttpResponseNotAllowed(['POST'])


@method_decorator(csrf_exempt, name='dispatch')
class OnboardingView(TemplateView):
    template_name = 'miniapp/questionarrie.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile and profile.onboarding_completed:
                return redirect('/')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_profile'] = profile
        return context


class UpdateProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        return self.request.user.profile


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class ProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'users/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context.update({
            'profile': profile,
            'total_workouts': 24,
            'total_calories': "5.2k",
            'total_weight': "8.5k",
            'total_time': "18h",
            'weekly_activity': [3, 5, 2, 6, 4, 7, 3],
            'current_weight': profile.weight,
            'weight_change': -2.5,
            'muscle_mass': {'current': 45.2, 'change': 1.8},
            'body_fat': {'current': 18.5, 'change': -2.1},
            'recent_workouts': [
                {'title': 'Upper Body Blast', 'date': 'Today, 10:30 AM', 'exercises': 12, 'duration': 45,
                 'calories': 320},
                {'title': 'Leg Day', 'date': 'Yesterday, 6:00 PM', 'exercises': 10, 'duration': 52, 'calories': 410},
                {'title': 'Core & Cardio', 'date': '2 days ago, 7:30 AM', 'exercises': 8, 'duration': 38,
                 'calories': 280},
            ]
        })
        return context
