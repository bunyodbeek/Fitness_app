from apps.views.bot_view import TelegramWebhookView
from apps.views.exercises import ExerciseDetailView, ExercisesByMuscleView, MuscleGroupListView
from apps.views.favorite import FavoritesListView, ToggleFavoriteView
from apps.views.users import TelegramAuthAPIView, UpdateProfileView, SettingsView, ProfileView, OnboardingView, \
    ProgressView, QuestionnaireSubmitAPIView
from apps.views.workouts import AnimationView, EditionDetailView, MyTrainerHistoryView, MyTrainerView, \
    ProgramDetailView, ProgramListView, WorkoutCompleteView, WorkoutDetailView, WorkoutStartView
