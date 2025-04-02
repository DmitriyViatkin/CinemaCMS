from django.db import models
from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    LANGUAGES_CHOICES = [
        ("ru", "RU"),
        ("ua", "UA"),
        ("en", "EN")
    ]
    GENDER_CHOICES = [
        ("man", "Man"),
        ("women","Women")
    ]
    nickname = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    languages = models.CharField(max_length=3, choices=LANGUAGES_CHOICES)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()

class Email_campaing(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ManyToManyField(Profile)
    text = models.TextField()
    status= models.CharField(max_length=20, choices=[("send","Відправлено"),("not sent","Не відправлено")])

class Tamplate_email(models.Model):
    id = models.AutoField(primary_key=True)
    email_campaign = models.ForeignKey(Email_campaing, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()