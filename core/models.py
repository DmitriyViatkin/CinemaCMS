from django.db import models
from users.models import User

from main.models import Block_SEO, Picture


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

    VIDEO_CHOISES= [
        ("2D", "2D"),
        ("3D", "3D"),
        ("imax", "IMAX")
    ]

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    genre = models.CharField(max_length=11, choices=GENRE_CHOISES, verbose_name= 'Жанр ')
    title = models.CharField(max_length=255, verbose_name= 'Назва')
    url_trailer = models.URLField(verbose_name= 'URL трелера ')
    description = models.TextField(verbose_name= 'Опис ')
    video_type = models.CharField(max_length=5, choices=VIDEO_CHOISES, verbose_name= 'Тип відео ')
    relise_date = models.DateField(verbose_name= 'Дата проката')
    age_limit = models.IntegerField(verbose_name= 'Вікова категорія')
    date = models.DateField(verbose_name= 'Дата')
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Зображення')

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Стрічка'
        verbose_name_plural = 'Стрічки'

class Cinemas(models.Model):

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name="SEO блок")
    title = models.CharField(max_length = 255, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    conditions = models.TextField(verbose_name="Умови")
    city = models.CharField(max_length=100, verbose_name="Місто")
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Картинки")
    date = models.DateField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатри'

class Halls(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name= 'Назва')
    cinema = models.ForeignKey(Cinemas, on_delete=models.CASCADE, related_name='halls', verbose_name="Кинотеатр")
    description = models.TextField(verbose_name= 'Опис')
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Зображення')
    date = models.DateField(auto_now_add=True, verbose_name= 'Дата')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Зали"

class Sessions(models.Model):

    id = models.AutoField(primary_key=True)
    hall_id = models.ForeignKey(Halls, on_delete=models.CASCADE, verbose_name= 'Зал')
    movie_id= models.ForeignKey(Movies, on_delete=models.CASCADE, verbose_name= 'Кіно')
    title = models.CharField(max_length=255, verbose_name= 'Назва')
    time_session = models.TimeField(verbose_name= 'Час сеансу')
    duration = models.TimeField(verbose_name= 'Тривалість')
    date = models.DateField(verbose_name= 'Дата')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеанси"



class Seats(models.Model):

    STATUS_CHOICES = [
        ("S", "Куплене"),
        ("F", "Вільне"),
        ("N", "Не доступно")
    ]
    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(Sessions, on_delete=models.CASCADE, verbose_name= 'сеанс')
    number_row = models.IntegerField(verbose_name= 'Номер ряда')
    seat = models.IntegerField(verbose_name= 'Номер місця')
    date = models.DateField(auto_now_add=True,verbose_name= 'Дата')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="F", verbose_name='Статус місця')
    halls = models.ForeignKey(Halls, on_delete=models.CASCADE, verbose_name='Зал')
    def __str__(self):
        return f'місце {self.number_row}, ряд {self.seat}'

    class Meta:
        verbose_name = "Місце"
        verbose_name_plural = "Місця"


class Tickets(models.Model):

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, related_name="tickets", null= True, verbose_name= 'Сеанс')
    seat = models.ForeignKey(Seats, on_delete=models.CASCADE, related_name="tickets",null= True, verbose_name= 'місце')
    profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tickets", null= True, verbose_name= 'Глядач')
    date = models.DateField(auto_now_add=True)
    halls = models.ForeignKey(Halls, on_delete=models.CASCADE, verbose_name= 'Зал')
    def __str__(self):
        session_title = self.session.title if self.session else "Немає сеансу"
        profile_name = self.profile.username if self.profile else "Немає глядача"
        return f"{session_title} ({profile_name})"
    class Meta:
        verbose_name = "Квиток"
        verbose_name_plural = "Квитки"