from rest_framework import serializers
from django.contrib.auth.models import User
from quiz.models import UserProfile, Question, Option, Quiz, Challenge, Answer
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'is_creator', 'created_on', 'updated_on']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password')
        user = User.objects.create(**user_data)
        user.set_password(password)  # Set the user's password
        user.save()
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        token, created = Token.objects.get_or_create(user=user)
        return user_profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user

        instance.is_creator = validated_data.get('is_creator',
                                                 instance.is_creator)
        instance.save()

        user.username = user_data.get('username', user.username)
        user.email = user_data.get('email', user.email)
        password = user_data.get('password', None)
        if password:
            user.set_password(password)
        user.save()
        return instance


class OptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option_text', 'is_correct']


class OptionUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct']


class QuestionCreateSerializer(serializers.ModelSerializer):
    options = OptionCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options']
        read_only_fields = ['created_by']

    def validate_options(self, options):
        if len(options) < 2:
            raise serializers.ValidationError(
                "At least two options are required.")

        correct_count = sum(1 for option in options if option.get('is_correct',
                                                                  False))
        if correct_count != 1:
            raise serializers.ValidationError(
                "Exactly one option must be marked as correct.")

        return options

    def create(self, validated_data):
        user_profile = self.context['request'].user.user
        options_data = validated_data.pop('options')
        question = Question.objects.create(created_by=user_profile,
                                           **validated_data)

        for option_data in options_data:
            Option.objects.create(question=question, **option_data)

        return question


class QuestionUpdateSerializer(serializers.ModelSerializer):
    options = OptionUpdateSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options']
        read_only_fields = ['created_by']

    def validate_options(self, options):
        if len(options) < 2:
            raise serializers.ValidationError(
                "At least two options are required.")

        correct_count = sum(1 for option in options if option.get('is_correct',
                                                                  False))
        if correct_count != 1:
            raise serializers.ValidationError(
                "Exactly one option must be marked as correct.")

        return options

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options')

        # Update existing options or create new ones
        existing_options = {option.id: option for option in instance.options.all()}
        updated_options = []

        for option_data in options_data:
            option_id = option_data.get('id')
            if option_id and option_id in existing_options:
                # Update existing option
                option = existing_options.pop(option_id)
                option.option_text = option_data.get('option_text',
                                                     option.option_text)
                option.is_correct = option_data.get('is_correct',
                                                    option.is_correct)
                option.save()
                updated_options.append(option)
            else:
                # Create new option
                option_data.pop('id', None)
                new_option = Option.objects.create(question=instance,
                                                   **option_data)
                updated_options.append(new_option)

        Option.objects.filter(question=instance).exclude(
            id__in=[opt.id for opt in updated_options]).update(is_active=False)

        # Update question text if provided
        instance.question_text = validated_data.get('question_text',
                                                    instance.question_text)
        instance.save()
        return instance


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), many=True)
    number_of_questions = serializers.SerializerMethodField()
    number_of_challenges = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions', 'number_of_questions', 'number_of_challenges']

    def get_number_of_questions(self, obj):
        return obj.get_number_of_questions()

    def get_number_of_challenges(self, obj):
        return obj.get_number_of_challenges()

    def validate_questions(self, value):
        user_profile = self.context['request'].user.user

        # Check that all questions belong to the logged-in user
        for question in value:
            if question.created_by != user_profile:
                raise serializers.ValidationError(
                    f"Question ID {question.id} does not belong to the logged-in user.")

        return value

    def create(self, validated_data):
        user_profile = self.context['request'].user.user
        questions_data = validated_data.pop('questions')
        quiz = Quiz.objects.create(user=user_profile, **validated_data)
        quiz.questions.set(questions_data)
        return quiz


class ChallengeSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source='user')
    quiz_id = serializers.PrimaryKeyRelatedField(
        queryset=Quiz.objects.all(), source='quiz')

    class Meta:
        model = Challenge
        fields = ['id', 'user_id', 'quiz_id']

    def validate(self, data):
        user = data['user']
        quiz = data['quiz']

        # Check if the user is a creator
        if user.is_creator:
            raise serializers.ValidationError(
                "Cannot assign quizzes to users who are creators.")

        # Check if the quiz has already been assigned to the user
        if Challenge.objects.filter(user=user, quiz=quiz).exists():
            raise serializers.ValidationError(
                "This quiz has already been assigned to this user.")

        return data

    def create(self, validated_data):
        challenge = Challenge.objects.create(**validated_data)
        return challenge


class AcceptChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['id']
        read_only_fields = ['user', 'quiz', 'created_on', 'finished_on']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'challenge', 'option']

    def validate(self, attrs):
        challenge = attrs.get('challenge')
        option = attrs.get('option')

        # Ensure the option belongs to the correct challenge's quiz
        if option.question not in challenge.quiz.questions.all():
            raise serializers.ValidationError(
                "The option does not belong to any question in this challenge's quiz.")

        return attrs


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    user_answered = serializers.SerializerMethodField()
    user_option = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options', 'user_answered',
                  'user_option']

    def get_user_answered(self, obj):
        request = self.context.get('request')
        if request:
            user_profile = request.user.user
            # Check if the user has answered this question in the 
            # context of the challenge
            return obj.options.filter(answer__challenge__user=user_profile).exists()
        return False

    def get_user_option(self, obj):
        request = self.context.get('request')
        if request:
            user_profile = request.user.user
            # Get the user's selected option for this question in the 
            # context of the challenge
            try:
                answer = Answer.objects.get(challenge__user=user_profile,
                                            option__question=obj)
                return answer.option.id
            except Answer.DoesNotExist:
                return None
        return None


class ChallengeDetailSerializer(serializers.ModelSerializer):
    quiz = serializers.PrimaryKeyRelatedField(read_only=True)
    questions = QuestionSerializer(many=True, source='quiz.questions.all',
                                   read_only=True)

    class Meta:
        model = Challenge
        fields = ['id', 'quiz', 'is_accepted', 'is_finished',
                  'no_of_correct_answers', 'questions', 'finished_on']


class UserAnswerSerializer(serializers.ModelSerializer):
    option = OptionSerializer()

    class Meta:
        model = Answer
        fields = ['option']


class FinishChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = ['is_finished', 'no_of_correct_answers', 'finished_on']
        read_only_fields = ['is_finished', 'no_of_correct_answers',
                            'finished_on']


class ChallengeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'