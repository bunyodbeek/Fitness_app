import traceback

import requests
from apps.forms import UserProfileForm
from apps.models import User, UserMotivation, UserProfile, Subscription
from apps.utils import bot_send_message
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import activate, get_language
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import TemplateView, UpdateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class QuestionnaireSubmitAPIView(APIView):
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
        data = request.data
        if data is None:
            return Response({'success': False, 'error': 'Noto‘g‘ri JSON format'}, status=400)

        telegram_id = data.get('telegram_id')
        if not telegram_id:
            return Response({'success': False, 'error': 'Telegram ID topilmadi'}, status=400)

        existing_profile = UserProfile.objects.filter(telegram_id=telegram_id).first()
        if existing_profile:
            return Response({
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

            login(request, user)
            bot_send_message(
                telegram_id,
                "🎉 **Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!** 🎉\n\n"
                "Sizning ma’lumotlaringiz saqlandi:\n"
                "━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Foydalanuvchi: {self.request.user.profile.name}\n"
                f"🆔 ID: {self.request.user.id}\n"
                "━━━━━━━━━━━━━━━━━━━\n\n"
                "💪 **Endi siz bizning Fitness Platformamizning to‘liq a’zosiz!**\n"
                "Sizga quyidagilar ochildi:\n"
                "• 🏋️‍♂️ Shaxsiy mashg‘ulotlar\n"
                "• 📅 Kunlik darslar rejalari\n"
                "• 🍎 Sog‘lom ovqatlanish bo‘yicha maslahatlar\n"
                "• 📊 Progress kuzatuv statistikasi\n\n"
                "🔥 *Bugun boshlang — ertangi kuningizni kuchliroq qiling!* 🏆"
            )

            return Response({
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
            return Response({'success': False, 'error': str(e)}, status=500)


class TelegramAuthAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            telegram_id = data.get('telegram_id')

            if not telegram_id:
                return Response({'success': False, 'error': 'Telegram ID not found'},
                                status=status.HTTP_400_BAD_REQUEST)

            profile = UserProfile.objects.filter(telegram_id=telegram_id).first()

            if profile:
                user = profile.user
                login(request, user)

                if profile.onboarding_completed:
                    return Response({
                        'success': True,
                        'redirect': reverse_lazy('animation'),
                        'onboarding_completed': True,
                        'user_id': user.id
                    })
                else:
                    return Response({
                        'success': True,
                        'redirect': reverse_lazy('onboarding'),
                        'onboarding_completed': False
                    })

            return Response({
                'success': True,
                'redirect': reverse_lazy('onboarding'),
                'onboarding_completed': False,
                'is_new_user': True
            })

        except Exception as e:
            print(traceback.format_exc())
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class OnboardingView(TemplateView):
    template_name = 'miniapp/questionarrie.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile and profile.onboarding_completed:
                return redirect('animation')
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
        subscription = Subscription.objects.filter(user=self.request.user.profile).first()
        context['days_remaining'] = subscription.days_remaining if subscription else 0
        # subscription_progres = (subscription.days_remaining / subscription.period()) * 100
        # context['subscription_progress'] = subscription_progres
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


class AdminPageView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_page/admin.html'


@method_decorator(csrf_protect, name='dispatch')
class ChangeLanguageView(LoginRequiredMixin, TemplateView):
    template_name = 'users/language.html'

    def _get_language_context(self):

        current_language = get_language()
        available_languages = []

        for code, name in settings.LANGUAGES:
            available_languages.append({
                'code': code,
                'name': str(name)
            })

        return {
            'current_language': current_language,
            'available_languages': available_languages,
        }

    def get(self, request, *args, **kwargs):

        context = self._get_language_context()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):

        new_language_code = request.POST.get('language')
        valid_codes = [lang[0] for lang in settings.LANGUAGES]

        if new_language_code and new_language_code in valid_codes:

            request.session['django_language'] = new_language_code

            activate(new_language_code)

            messages.success(request, _("Til muvaffaqiyatli saqlandi!"))

            response = HttpResponseRedirect(reverse('settings'))

            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, new_language_code)

            return response
        else:
            messages.error(request, _("Tanlangan til kodi noto'g'ri."))

            context = self._get_language_context()
            return render(request, self.template_name, context)
