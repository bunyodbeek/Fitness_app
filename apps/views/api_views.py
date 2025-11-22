import json

import requests
from apps.models import User, UserMotivation, UserProfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@csrf_exempt
@require_http_methods(["POST"])
def submit_questionnaire(request):
    """
    Questionnaire ma'lumotlarini qabul qilish
    """
    try:
        data = json.loads(request.body)

        telegram_id = data.get('telegram_id')
        gender = data.get('gender')
        experience = data.get('experience')
        goal = data.get('goal')
        motivation = data.get('motivation', [])
        days = data.get('days')
        weight = data.get('weight')

        print(f"✅ Questionnaire received from {telegram_id}")
        print(f"   Gender: {gender}")
        print(f"   Experience: {experience}")
        print(f"   Motivation: {motivation}")
        print(f"   Goal: {goal}")
        print(f"   Days: {days}")
        print(f"   Weight: {weight}")

        # TODO: Database'ga saqlash (keyinroq)

        return JsonResponse({
            'success': True,
            'message': 'Questionnaire saved successfully!',
            'redirect': ''
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth(request):
    """Telegram orqali authentication"""
    telegram_id = request.data.get('telegram_id')
    telegram_username = request.data.get('telegram_username', '')
    first_name = request.data.get('first_name', '')

    if not telegram_id:
        return Response({'error': 'telegram_id required'}, status=status.HTTP_400_BAD_REQUEST)

    # Premium statusni tekshirish
    is_premium = check_telegram_premium(telegram_id)

    # User yaratish yoki olish
    profile, created = UserProfile.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'telegram_username': telegram_username,
            'is_premium': is_premium,
            'name': first_name or telegram_username or 'User'
        }
    )

    # Agar user yo'q bo'lsa, yaratish
    if created and not profile.user:
        user = User.objects.create_user(
            username=f'tg_{telegram_id}',
            first_name=first_name
        )
        profile.user = user
        profile.save()

    return Response({
        'user_id': profile.user.id,
        'telegram_id': profile.telegram_id,
        'is_premium': profile.is_premium,
        'onboarding_completed': profile.onboarding_completed,
        'name': profile.name
    })


def check_telegram_premium(telegram_id):
    """Telegram premium statusni tekshirish"""
    # Bu yerda Telegram Bot API orqali tekshirasiz
    # Sizning bot tokeningiz kerak bo'ladi
    BOT_TOKEN = 'YOUR_BOT_TOKEN'  # settings.py dan oling

    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/getChatMember'
        params = {
            'chat_id': telegram_id,
            'user_id': telegram_id
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data.get('ok'):
            user_data = data.get('result', {}).get('user', {})
            return user_data.get('is_premium', False)
    except Exception as e:
        print(e)

    return False


def handle_gender(profile, value):
    profile.gender = value


def handle_experience(profile, value):
    profile.experience_level = value


def handle_goal(profile, value):
    profile.fitness_goal = value


def handle_motivation(profile, value):
    motivations = value if isinstance(value, list) else [value]

    UserMotivation.objects.filter(user=profile.user).delete()

    for m in motivations:
        UserMotivation.objects.create(user=profile.user, motivation=m)


def handle_days(profile, value):
    profile.workout_days_per_week = int(value)


def handle_weight(profile, value):
    profile.weight = float(value)


def handle_height(profile, value):
    profile.height = float(value)

@api_view(['POST'])
@permission_classes([AllowAny])
def save_onboarding_step(request):
    telegram_id = request.data.get('telegram_id')
    step = request.data.get('step')
    value = request.data.get('value')

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)

        handlers = {
            'gender': handle_gender,
            'experience': handle_experience,
            'goal': handle_goal,
            'motivation': handle_motivation,
            'days': handle_days,
            'weight': handle_weight,
            'height': handle_height,
        }

        handler = handlers.get(step)
        if handler is None:
            return Response(
                {'error': f'Unknown step: {step}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        handler(profile, value)
        profile.save()

        return Response({'success': True, 'message': 'Data saved successfully'})

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def complete_onboarding(request):
    """Onboarding jarayonini tugatish"""
    telegram_id = request.data.get('telegram_id')

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        profile.onboarding_completed = True
        profile.save()

        return Response({
            'success': True,
            'message': 'Onboarding completed',
            'profile': {
                'name': profile.name,
                'gender': profile.gender,
                'experience_level': profile.experience_level,
                'fitness_goal': profile.fitness_goal,
                'workout_days_per_week': profile.workout_days_per_week,
                'weight': str(profile.weight) if profile.weight else None,
                'height': str(profile.height) if profile.height else None,
            }
        })

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request):
    telegram_id = request.GET.get('telegram_id')

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        motivations = UserMotivation.objects.filter(user=profile.user).values_list('motivation', flat=True)

        return Response({
            'user_id': profile.user.id,
            'telegram_id': profile.telegram_id,
            'name': profile.name,
            'gender': profile.gender,
            'age': profile.age,
            'weight': str(profile.weight) if profile.weight else None,
            'height': str(profile.height) if profile.height else None,
            'bmi': profile.bmi,
            'experience_level': profile.experience_level,
            'fitness_goal': profile.fitness_goal,
            'motivations': list(motivations),
            'workout_days_per_week': profile.workout_days_per_week,
            'is_premium': profile.is_premium,
            'onboarding_completed': profile.onboarding_completed,
        })

    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
