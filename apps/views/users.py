import json
import traceback

import requests
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, UpdateView

from apps.forms import UserProfileForm
from apps.models import User, UserMotivation, UserProfile


class QuestionnaireSubmitView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            telegram_id = data.get('telegram_id')

            if not telegram_id:
                return JsonResponse({'success': False, 'error': 'Telegram ID topilmadi'}, status=400)

            existing_profile = UserProfile.objects.filter(telegram_id=telegram_id).first()
            if existing_profile:
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('program_list'),
                    'message': 'User already exists'
                })

            first_name = data.get('first_name', 'User')
            last_name = data.get('last_name', '')
            username = data.get('username', '')
            photo_url = data.get('photo_url', '')

            user, created = User.objects.get_or_create(
                username=f'telegram_{telegram_id}',
                defaults={'first_name': first_name, 'last_name': last_name}
            )

            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'telegram_id': telegram_id, 'name': first_name}
            )
            profile.telegram_id = telegram_id
            profile.telegram_username = username
            profile.name = first_name
            profile.gender = data.get('gender', 'male')
            profile.experience_level = data.get('experience', 'beginner')
            profile.fitness_goal = data.get('goal', 'build_body')
            profile.workout_days_per_week = int(data.get('days', 3))
            profile.weight = float(data.get('weight', 63))
            profile.onboarding_completed = True

            if photo_url:
                try:
                    response = requests.get(photo_url, timeout=5)
                    if response.status_code == 200:
                        profile.avatar.save(
                            f'telegram_{telegram_id}.jpg',
                            ContentFile(response.content),
                            save=False
                        )
                except Exception as e:
                    print(f"Avatar save error: {e}")

            profile.save()

            UserMotivation.objects.filter(user=user).delete()
            for motivation in data.get('motivation', []):
                UserMotivation.objects.create(user=user, motivation=motivation)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            return JsonResponse({
                'success': True,
                'message': 'Ma\'lumotlar muvaffaqiyatli saqlandi',
                'user_id': user.id,
                'username': user.username,
                'profile_id': profile.id,
                'telegram_id': telegram_id,
                'is_new_user': created
            })

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Noto‘g‘ri JSON format'}, status=400)

        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class TelegramAuthView(View):
    """Telegram WebApp orqali avtomatik login"""

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
                        'redirect': '/workouts/',
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


class OnboardingView(TemplateView):
    template_name = 'miniapp/questionarrie.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and profile.onboarding_completed:
                return redirect('/workouts/')
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
