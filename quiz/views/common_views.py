from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import generics
from quiz.models import Challenge
from quiz.serializers import ChallengeDetailSerializer
from quiz.permissions import IsChallengeOwnerOrQuizCreator
from rest_framework.permissions import IsAuthenticated


class LoginView(ObtainAuthToken):
    """
    Custom login view to authenticate users and return an auth token.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST request for user login.

        Returns:
            Response: JSON response with auth token, user ID, and email.
        """
        response = super(LoginView, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class ChallengeDetailView(generics.RetrieveAPIView):
    """
    Detail view for retrieving a single challenge instance.
    """
    queryset = Challenge.objects.all()
    serializer_class = ChallengeDetailSerializer
    permission_classes = [IsAuthenticated, IsChallengeOwnerOrQuizCreator]

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve details of a specific challenge.

        Returns:
            Response: JSON response with serialized challenge data.
        """
        instance = self.get_object()
        serializer = ChallengeDetailSerializer(instance,
                                               context={'request': request})
        return Response(serializer.data)
