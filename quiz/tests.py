from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from quiz.models import UserProfile, Question, Option

class AddQuestionViewTest(APITestCase):
    def setUp(self):
        # Create a user and authenticate
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user, is_creator=True)
        self.client.force_authenticate(user=self.user)

        self.url = reverse('add-question')

    def test_create_question_with_options(self):
        # Define valid question data with options
        data = {
            'question_text': 'What is the capital of France?',
            'options': [
                {'option_text': 'Paris', 'is_correct': True},
                {'option_text': 'London', 'is_correct': False}
            ]
        }

        response = self.client.post(self.url, data, format='json')

        # Check the response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the question was created
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.get()
        self.assertEqual(question.question_text, 'What is the capital of France?')

        # Check if the options were created
        self.assertEqual(Option.objects.count(), 2)
        option_texts = [option.option_text for option in Option.objects.all()]
        self.assertIn('Paris', option_texts)
        self.assertIn('London', option_texts)

    def test_create_question_with_insufficient_options(self):
        # Define invalid question data with only one option
        data = {
            'question_text': 'What is the capital of France?',
            'options': [
                {'option_text': 'Paris', 'is_correct': True}
            ]
        }

        response = self.client.post(self.url, data, format='json')

        # Check the response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the error message
        self.assertIn('At least two options are required.', str(response.data))

    def test_create_question_with_multiple_correct_options(self):
        # Define invalid question data with multiple correct options
        data = {
            'question_text': 'What is the capital of France?',
            'options': [
                {'option_text': 'Paris', 'is_correct': True},
                {'option_text': 'London', 'is_correct': True}
            ]
        }

        response = self.client.post(self.url, data, format='json')

        # Check the response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the error message
        self.assertIn('Exactly one option must be marked as correct.', str(response.data))

    def test_create_question_with_no_correct_options(self):
        # Define invalid question data with no correct options
        data = {
            'question_text': 'What is the capital of France?',
            'options': [
                {'option_text': 'Paris', 'is_correct': False},
                {'option_text': 'London', 'is_correct': False}
            ]
        }

        response = self.client.post(self.url, data, format='json')

        # Check the response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the error message
        self.assertIn('Exactly one option must be marked as correct.', str(response.data))
