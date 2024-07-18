from rest_framework import viewsets, generics
from quiz.models import UserProfile, Question, Quiz, Challenge
from quiz.serializers import (UserProfileSerializer, QuestionCreateSerializer,
                              QuestionUpdateSerializer, QuizSerializer,
                              ChallengeSerializer, ChallengeListSerializer)
from rest_framework.permissions import IsAuthenticated, AllowAny
from quiz.permissions import (IsQuestionOwner, IsCreator, IsQuizOwner)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling CRUD operations on UserProfile model.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        """
        Custom permissions based on the action (create or other CRUD operations).
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny,]
        else:
            self.permission_classes = [IsAuthenticated,]
        return super(UserProfileViewSet, self).get_permissions()


class AddQuestionView(generics.CreateAPIView):
    """
    API view for creating a new question.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionCreateSerializer
    permission_classes = [IsAuthenticated, IsCreator]


class EditQuestionView(generics.UpdateAPIView):
    """
    API view for updating an existing question.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionUpdateSerializer
    permission_classes = [IsAuthenticated, IsCreator]
    allowed_methods = ['PATCH']

    def update(self, request, *args, **kwargs):
        """
        Handle PATCH request to update a question partially.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Custom permissions based on request method (PATCH or others).
        """
        if self.request.method == 'PATCH':
            return [IsQuestionOwner()]
        return []


class QuestionListView(generics.ListAPIView):
    """
    API view for listing questions created by the authenticated user.
    """
    serializer_class = QuestionUpdateSerializer
    permission_classes = [IsAuthenticated, IsCreator]

    def get_queryset(self):
        """
        Return a queryset of questions created by the authenticated user.
        """
        user_profile = self.request.user.user
        queryset = Question.objects.filter(created_by=user_profile)
        return queryset


class QuizCreateView(generics.CreateAPIView):
    """
    API view for creating a new quiz.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsCreator]


class QuizListView(generics.ListAPIView):
    """
    API view for listing quizzes created by the authenticated user.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsCreator]

    def get_queryset(self):
        """
        Return a queryset of quizzes created by the authenticated user.
        """
        return self.queryset.filter(user=self.request.user.user)


class AssignChallengeView(generics.CreateAPIView):
    """
    API view for assigning a new challenge.
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    permission_classes = [IsAuthenticated, IsCreator]

    def perform_create(self, serializer):
        """
        Perform create action for assigning a challenge.
        """
        serializer.save()


class QuizChallengesListView(generics.ListAPIView):
    serializer_class = ChallengeListSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Check if the user has permission to access this quiz
        self.check_object_permissions(self.request, quiz)
        return Challenge.objects.filter(quiz=quiz)
