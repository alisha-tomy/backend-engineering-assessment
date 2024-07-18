from rest_framework import generics, status, serializers
from rest_framework.permissions import IsAuthenticated
from quiz.models import Challenge, Answer
from quiz.permissions import IsNotCreator
from rest_framework.response import Response
from quiz.serializers import (AcceptChallengeSerializer, AnswerSerializer,
                              ChallengeDetailSerializer,
                              FinishChallengeSerializer)
from django.utils import timezone


class AcceptChallengeView(generics.UpdateAPIView):
    """
    API view for accepting a challenge.
    """
    queryset = Challenge.objects.all()
    serializer_class = AcceptChallengeSerializer
    permission_classes = [IsAuthenticated, IsNotCreator]
    allowed_methods = ['PATCH']

    def get_queryset(self):
        """
        Return challenges that the authenticated user can accept.
        """
        return self.queryset.filter(user=self.request.user.user,
                                    is_accepted=False)

    def update(self, request, *args, **kwargs):
        """
        Handle PATCH request to accept a challenge.
        """
        instance = self.get_object()
        if instance.user != request.user.user:
            return Response({"detail":
                             "Not authorized to accept this challenge."},
                            status=status.HTTP_403_FORBIDDEN)
        instance.is_accepted = True
        instance.save()

        return Response({"detail": "Challenge accepted."},
                        status=status.HTTP_200_OK)


class AnswerQuizView(generics.CreateAPIView):
    """
    API view for answering a quiz within a challenge.
    """
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated, IsNotCreator]

    def perform_create(self, serializer):
        """
        Perform create action for saving an answer to a quiz question.
        """
        challenge_id = self.kwargs.get('challenge_id')
        challenge = Challenge.objects.get(id=challenge_id, user=self.request.user.user)

        if challenge.is_finished:
            raise serializers.ValidationError("This challenge has already been finished.")
        if not challenge.is_accepted:
            raise serializers.ValidationError("This challenge has not been accepted.")

        # Get the option and related question
        option = serializer.validated_data['option']
        question = option.question

        # Check for an existing answer for the same question in the challenge
        existing_answer = Answer.objects.filter(challenge=challenge, option__question=question).first()

        if existing_answer:
            # Update the existing answer
            existing_answer.option = option
            existing_answer.save()
        else:
            # Create a new answer if no existing answer is found
            serializer.save(challenge=challenge)

    def get_queryset(self):
        """
        Return answers submitted by the authenticated user.
        """
        return Answer.objects.filter(challenge__user=self.request.user.user)


class ChallengeListView(generics.ListAPIView):
    """
    API view for listing challenges created by the authenticated user.
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeDetailSerializer
    permission_classes = [IsAuthenticated, IsNotCreator]

    def get_queryset(self):
        """
        Return challenges created by the authenticated user.
        """
        return self.queryset.filter(user=self.request.user.user)


class FinishChallengeView(generics.UpdateAPIView):
    """
    API view for finishing a challenge.
    """
    queryset = Challenge.objects.all()
    serializer_class = FinishChallengeSerializer
    permission_classes = [IsAuthenticated, IsNotCreator]
    allowed_methods = ['PATCH']

    def get_queryset(self):
        """
        Return challenges that the authenticated user can finish.
        """
        return self.queryset.filter(user=self.request.user.user,
                                    is_finished=False)

    def update(self, request, *args, **kwargs):
        """
        Handle PATCH request to finish a challenge.
        """
        instance = self.get_object()
        if instance.user != request.user.user:
            return Response({"detail":
                             "Not authorized to finish this challenge."},
                            status=status.HTTP_403_FORBIDDEN)

        correct_answers = Answer.objects.filter(
            challenge=instance,
            option__is_correct=True
        ).count()
        instance.is_finished = True
        instance.finished_on = timezone.now()
        instance.no_of_correct_answers = correct_answers
        instance.save()
        return Response({"detail": "Challenge finished successfully"},
                        status=status.HTTP_200_OK)
