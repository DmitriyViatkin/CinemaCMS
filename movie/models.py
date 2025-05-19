from django.db import models

# Create your models here.
from main.models import Block_SEO, Gallery, Picture


class Movies(models.Model):
    GENRE_CHOISES = [
        ("DR", "Драма"),
        ("COM", "Комедія"),
        ("ACT", "Бойовик"),
        ("TR", "Трилер"),
        ("HOR", "Жахи"),
        ("Sci", "Фантастика"),
        ("FAN", "Фентезі"),
    ]

    VIDEO_CHOISES = [
        ("2D", "2D"),
        ("3D", "3D"),
        ("imax", "IMAX")
    ]

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name='Блок СЕО ')
    genre = models.CharField(max_length=11, choices=GENRE_CHOISES, verbose_name='Жанр ')
    title = models.CharField(max_length=255, verbose_name='Назва')
    url_trailer = models.URLField(verbose_name='URL трелера ')
    description = models.TextField(verbose_name='Опис ')
    video_type = models.CharField(max_length=5, choices=VIDEO_CHOISES, verbose_name='Тип відео ')
    relise_date = models.DateField(verbose_name='Дата проката')
    age_limit = models.IntegerField(verbose_name='Вікова категорія')
    date = models.DateField(verbose_name='Дата')

    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='movies', verbose_name='Галерея зображень')

    def __str__(self):
        return self.title


    class Meta:
        verbose_name = 'Кіно стрічка'
        verbose_name_plural = 'Кіно стрічки'
