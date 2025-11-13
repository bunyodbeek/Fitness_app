# apps/users/views.py

import json
import traceback

import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import activate
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from apps.models import PaymentHistory, User, UserMotivation, UserProfile


# ===== API ENDPOINTS =====

@method_decorator(csrf_exempt, name='dispatch')
class QuestionnaireSubmitView(View):

    def post(self, request):
        try:
            # JSON ma'lumotlarni olish
            data = json.loads(request.body)

            telegram_id = data.get('telegram_id')

            if not telegram_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Telegram ID topilmadi'
                }, status=400)

            existing_profile = UserProfile.objects.filter(telegram_id=telegram_id).first()
            if existing_profile:
                print(f"✅ Questionnaire data: {data}")
                print(f"👤 Telegram ID: {telegram_id}")
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('program_list'),
                    'message': 'User already exists'
                })

            first_name = data.get('first_name', 'User')
            last_name = data.get('last_name', '')
            username = data.get('username', '')
            photo_url = data.get('photo_url', '')

            # User topish yoki yaratish
            user, created = User.objects.get_or_create(
                username=f'telegram_{telegram_id}',
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )

            # Agar user allaqachon bor bo'lsa, ismni update qilish
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            # UserProfile yaratish yoki update qilish
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'telegram_id': telegram_id,
                    'name': first_name,
                }
            )

            # Ma'lumotlarni saqlash
            profile.telegram_id = telegram_id
            profile.telegram_username = username
            profile.name = first_name
            profile.gender = data.get('gender', 'male')
            profile.experience_level = data.get('experience', 'beginner')
            profile.fitness_goal = data.get('goal', 'build_body')
            profile.workout_days_per_week = int(data.get('days', 3))
            profile.weight = float(data.get('weight', 63))
            profile.onboarding_completed = True

            # Avatar ni saqlash (agar URL bor bo'lsa)
            if photo_url:
                try:
                    from django.core.files.base import ContentFile
                    response = requests.get(photo_url, timeout=5)
                    if response.status_code == 200:
                        profile.avatar.save(
                            f'telegram_{telegram_id}.jpg',
                            ContentFile(response.content),
                            save=False
                        )
                except Exception as e:
                    print(f"Avatar save error: {str(e)}")

            profile.save()

            # Motivations saqlash
            UserMotivation.objects.filter(user=user).delete()

            motivations = data.get('motivation', [])
            for motivation in motivations:
                UserMotivation.objects.create(
                    user=user,
                    motivation=motivation
                )

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
            return JsonResponse({
                'success': False,
                'error': 'Noto\'g\'ri JSON format'
            }, status=400)

        except Exception as e:
            print(f"ERROR: {str(e)}")
            print(traceback.format_exc())

            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@csrf_exempt
def telegram_auth_view(request):
    """
    Telegram WebApp dan kelgan user ni avtomatik login qilish
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_id = data.get('telegram_id')

            if telegram_id:
                try:
                    profile = UserProfile.objects.get(telegram_id=telegram_id)
                    user = profile.user

                    # Login qilish
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                    # Onboarding tugallanganmi?
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

                except UserProfile.DoesNotExist:
                    return JsonResponse({
                        'success': True,
                        'redirect': '/miniapp/questionnaire/',
                        'onboarding_completed': False,
                        'is_new_user': True
                    })

            return JsonResponse({
                'success': False,
                'error': 'Telegram ID not found'
            }, status=400)

        except Exception as e:
            print(f"Auth error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ===== ROOT SAHIFA =====

def home_view(request):
    """Home sahifasi"""
    return render(request, 'exercises/body_parts.html')


# ===== ONBOARDING =====

class OnboardingView(TemplateView):
    """Onboarding sahifasi - yangi foydalanuvchilar uchun"""
    template_name = 'miniapp/questionarrie.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Agar user allaqachon onboarding qilgan bo'lsa,
        to'g'ridan-to'g'ri /workouts/ ga yo'naltirish
        """
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                if profile.onboarding_completed:
                    return redirect('/workouts/')
            except UserProfile.DoesNotExist:
                pass

        return super().dispatch(request, *args, **kwargs)


# ===== PROFILE =====

class ProfileView(LoginRequiredMixin, TemplateView):
    """Profile asosiy sahifa"""
    template_name = 'users/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_profile'] = profile
        return context


class PersonalInfoView(LoginRequiredMixin, TemplateView):
    """Personal info sahifasi"""
    template_name = 'users/profile_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['user_profile'] = profile
        return context


class UpdateProfileView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'User not authenticated'
            }, status=401)

        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # 1. Name
        name = request.POST.get('name')
        if name:
            profile.name = name

        # 2. Gender
        gender = request.POST.get('gender')
        if gender in ['male', 'female']:
            profile.gender = gender

        # 3. Birth date
        birth_date = request.POST.get('birth_date')
        if birth_date:
            profile.birth_date = birth_date

        # 4. Weight
        weight = request.POST.get('weight')
        if weight:
            try:
                profile.weight = float(weight)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid weight value'}, status=400)

        # 5. Height
        height = request.POST.get('height')
        if height:
            try:
                profile.height = float(height)
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid height value'}, status=400)

        # 6. Unit system (optional)
        unit = request.POST.get('unit')
        if unit in ['metric', 'imperial']:
            profile.unit_system = unit

        # 7. Avatar (file)
        avatar = request.FILES.get('avatar')
        if avatar:
            profile.avatar = avatar

        # Save all updates
        profile.save()

        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})


# ===== SETTINGS =====

class SettingsView(LoginRequiredMixin, TemplateView):
    """Sozlamalar sahifasi"""
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class ChangeLanguageView(LoginRequiredMixin, View):
    """Tilni o'zgartirish"""

    def post(self, request):
        language = request.POST.get('language')
        if language in ['uz', 'en', 'ru']:
            profile = UserProfile.objects.get(user=request.user)
            profile.language = language
            profile.save()

            # Django tilini o'zgartirish
            activate(language)
            request.session['django_language'] = language

            messages.success(request, 'Til muvaffaqiyatli o\'zgartirildi!')
        return redirect('users:settings')


# ===== SUBSCRIPTION =====

class AccountManagementView(LoginRequiredMixin, TemplateView):
    """Obunani boshqarish"""
    template_name = 'users/account_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class SubscriptionInfoView(LoginRequiredMixin, TemplateView):
    """Obuna ma'lumotlari"""
    template_name = 'users/subscription_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        context['subscription_active'] = profile.is_subscribed
        context['days_left'] = profile.days_until_renewal
        return context


class PaymentHistoryView(LoginRequiredMixin, TemplateView):
    """To'lovlar tarixi"""
    template_name = 'users/payment_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payments = PaymentHistory.objects.filter(user=self.request.user)
        context['payments'] = payments
        return context


class CancelSubscriptionView(LoginRequiredMixin, View):
    """Obunani bekor qilish"""

    def post(self, request):
        profile = UserProfile.objects.get(user=request.user)
        profile.subscription_end_date = None
        profile.subscription_start_date = None
        profile.save()
        messages.success(request, 'Obuna bekor qilindi!')
        return redirect('users:account_management')


class RestoreSubscriptionView(LoginRequiredMixin, View):
    """Obunani qayta tiklash"""

    def post(self, request):
        # Bu yerda to'lov logikasi qo'shiladi
        messages.success(request, 'Obuna qayta tiklandi!')
        return redirect('users:account_management')


# ===== PROGRESS =====

class ProgressView(LoginRequiredMixin, TemplateView):
    """Progress tracking sahifasi"""
    template_name = 'users/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)

        # User profile
        context['profile'] = profile

        # Stats
        context['total_workouts'] = self.get_total_workouts()
        context['total_calories'] = self.get_total_calories()
        context['total_weight'] = self.get_total_weight_lifted()
        context['total_time'] = self.get_total_training_time()

        # Weekly activity data
        context['weekly_activity'] = self.get_weekly_activity()

        # Body measurements
        context['current_weight'] = profile.weight
        context['weight_change'] = self.get_weight_change()
        context['muscle_mass'] = self.get_muscle_mass()
        context['body_fat'] = self.get_body_fat_percentage()

        # Recent workouts
        context['recent_workouts'] = self.get_recent_workouts()

        return context

    def get_total_workouts(self):
        return 24

    def get_total_calories(self):
        return "5.2k"

    def get_total_weight_lifted(self):
        return "8.5k"

    def get_total_training_time(self):
        return "18h"

    def get_weekly_activity(self):
        return [3, 5, 2, 6, 4, 7, 3]

    def get_weight_change(self):
        return -2.5

    def get_muscle_mass(self):
        return {
            'current': 45.2,
            'change': 1.8
        }

    def get_body_fat_percentage(self):
        return {
            'current': 18.5,
            'change': -2.1
        }

    def get_recent_workouts(self):
        return [
            {
                'title': 'Upper Body Blast',
                'date': 'Today, 10:30 AM',
                'exercises': 12,
                'duration': 45,
                'calories': 320
            },
            {
                'title': 'Leg Day',
                'date': 'Yesterday, 6:00 PM',
                'exercises': 10,
                'duration': 52,
                'calories': 410
            },
            {
                'title': 'Core & Cardio',
                'date': '2 days ago, 7:30 AM',
                'exercises': 8,
                'duration': 38,
                'calories': 280
            }
        ]
