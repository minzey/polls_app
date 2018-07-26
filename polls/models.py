from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)

class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=200)

class AccessToken(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_token = models.CharField(max_length=200, null=True)
    voting_token = models.CharField(max_length=200, null=True)
