from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    LANGUAGES_CHOICES = [
        ("ru", "RU"),
        ("ua", "UA"),
        ("en", "EN")
    ]
    GENDER_CHOICES = [
        ("man", "Man"),
        ("women","Women")
    ]
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    languages = models.CharField(max_length=3, choices=LANGUAGES_CHOICES)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

class Email_campaing(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ManyToManyField(User, verbose_name="Користувачі")
    status = models.CharField(
        max_length=20,
        choices=[("send", "Відправлено"), ("not sent", "Не відправлено")],
        default="not sent",
        verbose_name="Статус"
    )

    template = models.ForeignKey(
        'Tamplate_email',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Шаблон Email"
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Email кампанія"
        verbose_name_plural = "Email кампанії"
        ordering = ['-created_at']

    def __str__(self):
        return f"Кампанія #{self.id} ({self.get_status_display()})"

class Tamplate_email(models.Model):
    id = models.AutoField(primary_key=True)

    email_campaign = models.ForeignKey(Email_campaing, on_delete=models.CASCADE, verbose_name="Email Кампания", null=True, blank=True, related_name='associated_templates')


    template_file = models.FileField(
        upload_to='email_templates/',
        verbose_name="Файл шаблона Email"
    )

    class Meta:
        verbose_name = "Шаблон email"
        verbose_name_plural = "Шаблоны email"