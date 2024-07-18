from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT,
                                related_name='user')
    is_creator = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Question(BaseModel):
    question_text = models.TextField()
    created_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question_text',)

    def __str__(self):
        return f"{self.id} - {self.question_text[:50]}"


class Option(BaseModel):
    option_text = models.TextField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 related_name="options")
    is_correct = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('question', 'option_text')

    def __str__(self):
        return f"{self.id} - {self.option_text[:50]}"


class Quiz(BaseModel):
    title = models.TextField()
    description = models.TextField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question, related_name="quizzes")

    def __str__(self):
        return f"{self.id} - {self.title}"

    def get_number_of_questions(self):
        return self.questions.count()

    def get_number_of_challenges(self):
        return self.challenges.count()


class Challenge(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,
                             related_name="challenges")
    is_accepted = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)
    no_of_correct_answers = models.IntegerField(null=True, blank=True)
    finished_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'quiz')

    def __str__(self):
        return f"{self.user} - {self.quiz.title}"


class Answer(BaseModel):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE,
                                  related_name="user_answers")
    option = models.ForeignKey(Option, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["challenge", "option"]]

    def __str__(self):
        return f"Challenge: {self.challenge} - Option: {self.option.option_text[:50]}"
