from django.urls import path, include
from rest_framework.routers import DefaultRouter
from quiz.views import creator_views
from quiz.views import common_views
from quiz.views import user_views

router = DefaultRouter()
router.register(r'user-profiles', creator_views.UserProfileViewSet)


urlpatterns = [
    # Admin URL patterns

    path('', include(router.urls)),
    path('questions/add/', creator_views.AddQuestionView.as_view(),
         name='add-question'),
    path('questions/edit/<int:pk>/',
         creator_views.EditQuestionView.as_view(), name='edit-question'),
    path('questions/', creator_views.QuestionListView.as_view(),
         name='question-list'),
    path('quiz/create/', creator_views.QuizCreateView.as_view(),
         name='quiz-create'),
    path('challenge/assign/',
         creator_views.AssignChallengeView.as_view(),
         name='assign-challenge'),
    path('quizzes/', creator_views.QuizListView.as_view(),
         name='quiz-list'),
    path('quizzes/<int:quiz_id>/challenges/',
         creator_views.QuizChallengesListView.as_view(),
         name='quiz-challenges'),


    # Common URL patterns

    path('login/', common_views.LoginView.as_view(), name='login'),
    path('challenges/<int:pk>/',
         common_views.ChallengeDetailView.as_view(),
         name='challenge-detail'),

    # End User URL patterns

    path('challenges/accept/<int:pk>/',
         user_views.AcceptChallengeView.as_view(),
         name='accept-challenge'),
    path('challenges/<int:challenge_id>/answer/',
         user_views.AnswerQuizView.as_view(), name='answer-quiz'),
    path('challenge/<int:pk>/finish/',
         user_views.FinishChallengeView.as_view(),
         name='finish-challenge'),
    path('challenges/', user_views.ChallengeListView.as_view(),
         name='challenge-list'),

]
