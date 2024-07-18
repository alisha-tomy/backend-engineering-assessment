from rest_framework import permissions


class IsQuestionOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a question to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user making the request is the owner of the question
        return obj.created_by.user == request.user


class IsCreator(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user.user.is_creator


class IsNotCreator(permissions.BasePermission):
    """
    Custom permission to allow only users with is_creator=False.
    """

    def has_permission(self, request, view):
        return request.user.user.is_creator == False


class IsChallengeOwnerOrQuizCreator(permissions.BasePermission):
    """
    Custom permission to only allow owners of the 
    challenge or creators of the quiz to access.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the request user is the owner of the challenge or creator of the quiz
        return request.user == obj.user.user or request.user == obj.quiz.user.user
    

class IsQuizOwner(permissions.BasePermission):
    """
    Custom permission to allow only users with is_creator=False.
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user.user
