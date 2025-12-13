from django.urls import path

from apps.bot.bot_view import TelegramWebhookView
from apps.views import (
    AnimationView,
    EditionDetailView,
    ExerciseDetailView,
    ExercisesByMuscleView,
    FavoritesListView,
    MuscleGroupListView,
    MyTrainerHistoryView,
    MyTrainerView,
    OnboardingView,
    ProfileView,
    ProgramDetailView,
    ProgramListView,
    ProgressView,
    QuestionnaireSubmitAPIView,
    SettingsView,
    TelegramAuthAPIView,
    ToggleFavoriteView,
    UpdateProfileView,
    WorkoutCompleteView,
    WorkoutDetailView,
    WorkoutStartView,
)
from apps.views.favorite import FavoriteToggleAPIView, CreateCollectionView
from apps.views.payments import PaymentHistoryListView, ManageSubscriptionListView
from apps.views.users import AdminPageView, ChangeLanguageView

urlpatterns = [
    path('exercises/', MuscleGroupListView.as_view(), name='muscle_groups'),
    path('exercises/<str:muscle>/', ExercisesByMuscleView.as_view(), name='exercises_by_muscle'),
    path('exercises/detail/<int:exercise_id>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    path('exercises/favorite/toggle/<int:exercise_id>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', FavoritesListView.as_view(), name='favorite_list_page'),
    path('api/questionnaire/submit/', QuestionnaireSubmitAPIView.as_view(), name='questionnaire_submit'),

    path('api/telegram-auth/', TelegramAuthAPIView.as_view(), name='telegram_auth'),
    path('miniapp/questionnaire/', OnboardingView.as_view(), name='onboarding'),
    path('users/profile/', ProfileView.as_view(), name='user_profile'),
    path('user/progress/', ProgressView.as_view(), name='user_progress'),

    path('users/profile/update/', UpdateProfileView.as_view(), name='profile_update'),
    path('users/settings/', SettingsView.as_view(), name='settings'),

    path('workout/', ProgramListView.as_view(), name='program_list'),
    path('', AnimationView.as_view(), name='animation'),
    path('program/<int:pk>/', ProgramDetailView.as_view(), name='program_detail'),
    path('edition/<int:pk>/', EditionDetailView.as_view(), name='edition_detail'),
    path('workout/<int:pk>/', WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/<int:pk>/start/', WorkoutStartView.as_view(), name='workout_start'),
    path('workout/<int:pk>/complete/', WorkoutCompleteView.as_view(), name='workout_complete'),

    path('my-trainer/', MyTrainerView.as_view(), name='my_trainer'),
    path('my-trainer/history/', MyTrainerHistoryView.as_view(), name='my_trainer_history'),
    path('workout/<int:session_id>/detail/', WorkoutDetailView.as_view(), name='workout_session_detail'),

    path("bot/webhook/", TelegramWebhookView.as_view(), name="telegram_webhook"),

    path('panel/', AdminPageView.as_view(), name='admin_page'),

    path('favorites/collection/<int:collection_id>/toggle/', FavoriteToggleAPIView.as_view(), name='favorite-toggle'),

    path("create/collection/", CreateCollectionView.as_view(), name="favorites"),

    path('change/language/', ChangeLanguageView.as_view(), name='change_language'),

    path('manage/subscription/', ManageSubscriptionListView.as_view(), name='manage_subscription'),

    path('payment/history/', PaymentHistoryListView.as_view(), name='payment_history'),
]
