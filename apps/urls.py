from apps.views.api_views import get_user_profile, complete_onboarding, save_onboarding_step, telegram_auth
from apps.views.exercises import ExercisesByMuscleView, ExerciseDetailView, MuscleGroupListView
from django.urls import path

from apps.views.favorite import RemoveFavoriteView, ToggleFavoriteView, FavoritesListView
from apps.views.users import SettingsView, UpdateProfileView, ProgressView, OnboardingView, TelegramAuthView, \
    QuestionnaireSubmitView, ProfileView
from apps.views.workouts import WorkoutCompleteView, WorkoutStartView, EditionDetailView, ProgramDetailView, \
    AnimationView, ProgramListView

urlpatterns = [

    path('exercises/', MuscleGroupListView.as_view(), name='muscle_groups'),
    path('exercises/<str:muscle>/', ExercisesByMuscleView.as_view(), name='exercises_by_muscle'),
    path('exercises/detail/<int:exercise_id>/', ExerciseDetailView.as_view(), name='exercise_detail'),
    path('favorite/toggle/<int:exercise_id>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', FavoritesListView.as_view(), name='favorites'),
    path('exercises/favorite/toggle/<int:exercise_id>/', ToggleFavoriteView.as_view(),
         name='toggle_favorite'),
    path('favorites/remove/<int:favorite_id>/', RemoveFavoriteView.as_view(), name='remove_favorite'),

    path('api/questionnaire/submit/', QuestionnaireSubmitView.as_view(), name='questionnaire_submit'),
    path('api/telegram-auth/', TelegramAuthView.as_view(), name='telegram_auth'),
    path('miniapp/questionnaire/', OnboardingView.as_view(), name='onboarding'),
    path('users/profile/', ProfileView.as_view(), name='user_profile'),
    path('user/progress/', ProgressView.as_view(), name='user_progress'),

    path('users/profile/update/', UpdateProfileView.as_view(), name='profile_update'),
    path('users/settings/', SettingsView.as_view(), name='settings'),

    path('workout/', ProgramListView.as_view(), name='program_list'),
    path('', AnimationView.as_view(), name='animation'),
    path('program/<int:pk>/', ProgramDetailView.as_view(), name='program_detail'),
    path('edition/<int:pk>/', EditionDetailView.as_view(), name='edition_detail'),
    # path('workout/<int:pk>/', WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/<int:pk>/start/', WorkoutStartView.as_view(), name='workout_start'),
    path('workout/<int:pk>/complete/', WorkoutCompleteView.as_view(), name='workout_complete'),


    path('api/users/auth/', telegram_auth, name='telegram_auth_api'),
    path('api/users/onboarding/save/', save_onboarding_step, name='save_onboarding_step'),
    path('api/users/onboarding/complete/', complete_onboarding, name='complete_onboarding'),
    path('api/users/profile/', get_user_profile, name='get_user_profile'),
]
