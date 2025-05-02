from django.db import models
from users.models import User
from main.models import Block_SEO, Gallery
from movie.models import Movies


class Cinemas(models.Model):

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name="SEO блок")
    title = models.CharField(max_length = 255, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    conditions = models.TextField(verbose_name="Умови")
    city = models.CharField(max_length=100, verbose_name="Місто")
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    date = models.DateField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатри'


class Halls(models.Model):
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name="SEO блок")
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='Назва')
    cinema = models.ForeignKey(Cinemas, on_delete=models.CASCADE, related_name='halls', verbose_name="Кинотеатр")
    description = models.TextField(verbose_name='Опис')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Картинка')
    date = models.DateField(auto_now_add=True, verbose_name='Дата')

    rows = models.PositiveIntegerField(verbose_name='Кількість рядів', null=True, blank=True)
    seats_row = models.PositiveIntegerField(verbose_name='Місць у ряду', null=True, blank=True)

    def total_seats(self):
        """Общее количество мест в зале"""
        if self.rows and self.seats_per_row:
            return self.rows * self.seats_per_row
        return 0

    def __str__(self):
        return f"{self.title} ({self.cinema})"

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Зали"

class Sessions(models.Model):

    id = models.AutoField(primary_key=True)
    cinema = models.ForeignKey(Cinemas, on_delete=models.CASCADE, related_name='sessions', verbose_name="Кинотеатр")
    hall_id = models.ForeignKey(Halls, on_delete=models.CASCADE, verbose_name= 'Зал')
    movie = models.ForeignKey(Movies, on_delete=models.SET_NULL, null=True, blank=True)
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
        profile_name = self.user.username if self.profile else "Немає глядача"
        return f"{session_title} ({profile_name})"
    class Meta:
        verbose_name = "Квиток"
        verbose_name_plural = "Квитки"