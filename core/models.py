from django.db import models
from users.models import User
from main.models import Block_SEO, Gallery
from movie.models import Movies
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

class Cinemas(models.Model):

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name="SEO блок")
    title = models.CharField(max_length = 255, verbose_name=_("Назва"))
    description = models.TextField(verbose_name=_("Опис"))
    conditions = models.TextField(verbose_name=_("Умови"))
    city = models.CharField(max_length=100, verbose_name=_("Місто"))
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
    scheme_hall = models.FileField(upload_to='scheme_hall/')
    title = models.CharField(max_length=255, verbose_name=_('Назва'))
    cinema = models.ForeignKey(Cinemas, on_delete=models.CASCADE, related_name='halls', verbose_name="Кинотеатр")
    description = models.TextField(verbose_name=_('Опис'))
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Картинка')
    date = models.DateField(auto_now_add=True, verbose_name='Дата')



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
    hall_id = models.ForeignKey(Halls, on_delete=models.CASCADE,related_name='sessions', verbose_name= 'Зал')
    movie = models.ForeignKey(Movies, on_delete=models.SET_NULL, related_name='movie_sessions',null=True, blank=True)

    time_session = models.TimeField(verbose_name= 'Час сеансу')
    duration = models.TimeField(verbose_name= 'Тривалість')
    date = models.DateField(verbose_name= 'Дата')


    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеанси"


class Seats(models.Model):
    STATUS_CHOICES = [
        ("S", _("Куплене")),
        ("F", _("Вільне")),
        ("N", _("Не доступно"))
    ]

    id = models.AutoField(primary_key=True)

    number_row = models.IntegerField(verbose_name=_('Номер ряду'))
    seat = models.IntegerField(verbose_name=_('Номер місця'))
    date = models.DateField(auto_now_add=True, verbose_name=_('Дата'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="F", verbose_name=_('Статус місця'))
    halls = models.ForeignKey('Halls', on_delete=models.CASCADE, related_name='seats_in_hall', verbose_name=_('Зал'))

    is_vip = models.BooleanField(default=False, verbose_name=_('VIP'))
    price = models.DecimalField(max_digits=8, decimal_places=2, default=120.00, verbose_name=_('Ціна'))

    class Meta:
        unique_together = ('halls', 'number_row', 'seat')
        verbose_name = _("Місце")
        verbose_name_plural = _("Місця")
        ordering = ['number_row', 'seat']

    def __str__(self):
        return f'ряд {self.number_row}, місце {self.seat}'

class Tickets(models.Model):

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, related_name="tickets", null= True, verbose_name= 'Сеанс')
    movie = models.ForeignKey(Movies, on_delete=models.SET_NULL, null=True, blank=True)
    seat = models.ForeignKey(Seats, on_delete=models.CASCADE, related_name="tickets",null= True, verbose_name= 'місце')
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets", null= True, verbose_name= 'Глядач')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата та час покупки')
    halls = models.ForeignKey(Halls, on_delete=models.CASCADE, verbose_name= 'Зал')
    def __str__(self):
        session_title = self.session.title if self.session else "Немає сеансу"
        profile_name = self.user.username if self.profile else "Немає глядача"
        return f"{session_title} ({profile_name})"
    class Meta:
         verbose_name = "Квиток"
         verbose_name_plural = "Квитки"
         constraints = [

                    UniqueConstraint(fields=['session', 'seat'], name='unique_ticket_session_seat')
                ]