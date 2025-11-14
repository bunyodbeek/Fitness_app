from django.urls import path

from apps.views import api_views, exercises, favorite, payments, users, workouts

urlpatterns = [
    # Exercises
    path('exercises/', exercises.MuscleGroupListView.as_view(), name='muscle_groups'),
    path('exercises/muscle/<int:muscle_id>/', exercises.ExercisesByMuscleView.as_view(), name='exercises_by_muscle'),
    path('exercises/all/', exercises.AllExercisesView.as_view(), name='all_exercises'),
    path('exercises/<int:exercise_id>/', exercises.ExerciseDetailView.as_view(), name='exercise_detail'),
    path('favorites/', favorite.FavoritesView.as_view(), name='favorites'),
    path('favorites/toggle/<str:content_type>/<int:object_id>/', favorite.ToggleFavoriteView.as_view(),
         name='toggle_favorite'),
    path('favorites/remove/<int:favorite_id>/', favorite.RemoveFavoriteView.as_view(), name='remove_favorite'),

    path('click/prepare/', payments.click_prepare, name='click_prepare'),
    path('click/complete/', payments.click_complete, name='click_complete'),
    path('click/card-token/', payments.click_card_token_callback, name='click_card_token'),
    path('subscribe/', payments.subscribe_view, name='subscribe'),
    path('create-payment/', payments.create_payment, name='create_payment'),
    path('add-card/', payments.add_card_view, name='add_card'),
    path('remove-card/', payments.remove_card, name='remove_card'),
    path('success/', payments.payment_success, name='success'),
    path('failed/', payments.payment_failed, name='failed'),

    path('api/questionnaire/submit/', users.QuestionnaireSubmitView.as_view(), name='questionnaire_submit'),
    path('api/telegram-auth/', users.TelegramAuthView.as_view(), name='telegram_auth'),
    path('miniapp/questionnaire/', users.OnboardingView.as_view(), name='onboarding'),
    path('users/profile/', users.ProfileView.as_view(), name='user_profile'),
    path('user/progress/', users.ProgressView.as_view(), name='user_progress'),
    path('users/profile/personal-info/', users.PersonalInfoView.as_view(), name='personal_info'),
    path('users/profile/update-name/', users.UpdateProfileView.as_view(), name='update_name'),
    path('users/profile/update-gender/', users.UpdateProfileView.as_view(), name='update_gender'),
    path('users/profile/update-birth-date/', users.UpdateProfileView.as_view(), name='update_birth_date'),
    path('users/profile/update-weight/', users.UpdateProfileView.as_view(), name='update_weight'),
    path('users/profile/update-height/', users.UpdateProfileView.as_view(), name='update_height'),
    path('users/profile/update-avatar/', users.UpdateProfileView.as_view(), name='update_avatar'),
    path('users/settings/', users.SettingsView.as_view(), name='settings'),
    path('users/settings/change-language/', users.ChangeLanguageView.as_view(), name='change_language'),
    path('users/settings/account-management/', users.AccountManagementView.as_view(), name='account_management'),
    path('users/settings/subscription-info/', users.SubscriptionInfoView.as_view(), name='subscription_info'),
    path('users/settings/payment-history/', users.PaymentHistoryView.as_view(), name='payment_history'),
    path('users/settings/cancel-subscription/', users.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('users/settings/restore-subscription/', users.RestoreSubscriptionView.as_view(), name='restore_subscription'),

    path('', workouts.ProgramListView.as_view(), name='program_list'),
    path('program/<int:pk>/', workouts.ProgramDetailView.as_view(), name='program_detail'),
    path('edition/<int:pk>/', workouts.EditionDetailView.as_view(), name='edition_detail'),
    path('workout/<int:pk>/', workouts.WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/<int:pk>/start/', workouts.WorkoutStartView.as_view(), name='workout_start'),
    path('workout/<int:pk>/complete/', workouts.WorkoutCompleteView.as_view(), name='workout_complete'),

    # ApiViews
    path('api/users/auth/', api_views.telegram_auth, name='telegram_auth_api'),
    path('api/users/onboarding/save/', api_views.save_onboarding_step, name='save_onboarding_step'),
    path('api/users/onboarding/complete/', api_views.complete_onboarding, name='complete_onboarding'),
    path('api/users/profile/', api_views.get_user_profile, name='get_user_profile'),
]
