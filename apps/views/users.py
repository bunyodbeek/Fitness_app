import json
import traceback

import requests
from apps.models import PaymentHistory, User, UserMotivation, UserProfile
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import activate
from django.views import View
from django.views.generic import TemplateView


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

            # 🔹 Foydalanuvchi ma'lumotlari
            first_name = data.get('first_name', 'User')
            last_name = data.get('last_name', '')
            username = data.get('username', '')
            photo_url = data.get('photo_url', '')

            # 🔹 User yaratish yoki topish
            user, created = User.objects.get_or_create(
                username=f'telegram_{telegram_id}',
                defaults={'first_name': first_name, 'last_name': last_name}
            )

            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            # 🔹 Profil yaratish yoki yangilash
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

            # 🔹 Avatar yuklash
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

            # 🔹 Motivatsiyalarni yangilash
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


# =======================
# 🔐 TELEGRAM AUTH
# =======================

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


# =======================
# 🏠 HOME
# =======================

class HomeView(TemplateView):
    """Asosiy sahifa"""
    template_name = 'exercises/body_parts.html'


# =======================
# 🧭 ONBOARDING
# =======================

class OnboardingView(TemplateView):
    """Yangi foydalanuvchilar uchun onboarding"""
    template_name = 'miniapp/questionarrie.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and profile.onboarding_completed:
                return redirect('/workouts/')
        return super().dispatch(request, *args, **kwargs)


# =======================
# 👤 PROFILE
# =======================

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_profile'] = profile
        return context


class PersonalInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_profile'] = profile
        return context


class UpdateProfileView(LoginRequiredMixin, View):
    """Profilni yangilash"""

    def post(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

        fields = ['name', 'gender', 'birth_date', 'weight', 'height', 'unit']
        for field in fields:
            val = request.POST.get(field)
            if val:
                setattr(profile, field, val)

        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        try:
            if profile.weight:
                profile.weight = float(profile.weight)
            if profile.height:
                profile.height = float(profile.height)
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid numeric value'}, status=400)

        profile.save()
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})


# =======================
# ⚙️ SETTINGS
# =======================

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class ChangeLanguageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        language = request.POST.get('language')
        if language in ['uz', 'en', 'ru']:
            profile = UserProfile.objects.get(user=request.user)
            profile.language = language
            profile.save()
            activate(language)
            request.session['django_language'] = language
            messages.success(request, "Til muvaffaqiyatli o‘zgartirildi!")
        return redirect('users:settings')


# =======================
# 💳 SUBSCRIPTION
# =======================

class AccountManagementView(LoginRequiredMixin, TemplateView):
    template_name = 'users/account_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class SubscriptionInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'users/subscription_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context.update({
            'profile': profile,
            'subscription_active': profile.is_subscribed,
            'days_left': profile.days_until_renewal
        })
        return context


class PaymentHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'users/payment_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = PaymentHistory.objects.filter(user=self.request.user.profile)
        return context


class CancelSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user.profile)
        profile.subscription_end_date = None
        profile.subscription_start_date = None
        profile.save()
        messages.success(request, 'Obuna bekor qilindi!')
        return redirect('users:account_management')


class RestoreSubscriptionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Obuna qayta tiklandi!')
        return redirect('users:account_management')


# =======================
# 📈 PROGRESS
# =======================

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
