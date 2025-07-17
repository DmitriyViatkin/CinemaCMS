from django.db import models

# Create your models here.
from main.models import Block_SEO, Gallery, Picture
from django.utils.translation import gettext_lazy as _


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



    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name='Блок СЕО ')
    genre = models.CharField(max_length=11, choices=GENRE_CHOISES, verbose_name='Жанр ')
    title = models.CharField(max_length=255, verbose_name=_('Назва'))
    url_trailer = models.URLField(verbose_name=_('URL трейлера'))
    description = models.TextField(verbose_name=_('Опис'))

    relise_date = models.DateField(verbose_name=_('Дата проката'))
    age_limit = models.PositiveIntegerField(verbose_name=_('Вікова категорія'))
    date = models.DateField(auto_now_add=True, verbose_name=_('Дата створення запису'))
    is_2d =  models.BooleanField(default=False, verbose_name='2D')
    is_3d = models.BooleanField(default=False, verbose_name='3D')
    is_imax = models.BooleanField(default=False, verbose_name='IMAX')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='movies', verbose_name=_('Галерея зображень'))


    def __str__(self):
        return self.title

    def get_youtube_embed_url(self):

        if self.url_trailer:

            import re
            match = re.search(r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})',                self.url_trailer)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/embed/{video_id}"
        return None

    def __str__(self):
        return self.title


    class Meta:
        verbose_name = 'Кіно стрічка'
        verbose_name_plural = 'Кіно стрічки'
