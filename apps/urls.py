from apps.views import api_views, exercises, favorite, users, workouts
from apps.views.exercises import ExercisesByMuscleView, ToggleFavoriteView
from django.urls import path

urlpatterns = [

    path('exercises/', exercises.MuscleGroupListView.as_view(), name='muscle_groups'),
    path('exercises/<str:muscle>/', ExercisesByMuscleView.as_view(), name='exercises_by_muscle'),
    path('exercises/all/', exercises.AllExercisesView.as_view(), name='all_exercises'),
    path('exercises/detail/<int:exercise_id>/', exercises.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('favorite/toggle/<int:exercise_id>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('favorites/', favorite.FavoritesView.as_view(), name='favorites'),
    path('exercises/favorite/toggle/<int:exercise_id>/', exercises.ToggleFavoriteView.as_view(),
         name='toggle_favorite'),
    path('favorites/remove/<int:favorite_id>/', favorite.RemoveFavoriteView.as_view(), name='remove_favorite'),

    path('api/questionnaire/submit/', users.QuestionnaireSubmitView.as_view(), name='questionnaire_submit'),
    path('api/telegram-auth/', users.TelegramAuthView.as_view(), name='telegram_auth'),
    path('miniapp/questionnaire/', users.OnboardingView.as_view(), name='onboarding'),
    path('users/profile/', users.ProfileView.as_view(), name='user_profile'),
    path('user/progress/', users.ProgressView.as_view(), name='user_progress'),

    path('users/profile/update/', users.UpdateProfileView.as_view(), name='profile_update'),
    path('users/settings/', users.SettingsView.as_view(), name='settings'),

    path('workout/', workouts.ProgramListView.as_view(), name='program_list'),
    path('', workouts.AnimationView.as_view(), name='animation'),
    path('program/<int:pk>/', workouts.ProgramDetailView.as_view(), name='program_detail'),
    path('edition/<int:pk>/', workouts.EditionDetailView.as_view(), name='edition_detail'),
    path('workout/<int:pk>/', workouts.WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/<int:pk>/start/', workouts.WorkoutStartView.as_view(), name='workout_start'),
    path('workout/<int:pk>/complete/', workouts.WorkoutCompleteView.as_view(), name='workout_complete'),


    path('api/users/auth/', api_views.telegram_auth, name='telegram_auth_api'),
    path('api/users/onboarding/save/', api_views.save_onboarding_step, name='save_onboarding_step'),
    path('api/users/onboarding/complete/', api_views.complete_onboarding, name='complete_onboarding'),
    path('api/users/profile/', api_views.get_user_profile, name='get_user_profile'),
]
