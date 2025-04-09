from django.db import models
from users.models import Profile

from main.models import Block_SEO, Picture


class Movies(models.Model):
    GENRE_CHOISES = [
        ("DR", "Драма"),
        ("COM", "Комедія"),
        ("ACT",  "Бойовик"),
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
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE)
    genre = models.CharField(max_length=11, choices=GENRE_CHOISES)
    title = models.CharField(max_length=255)
    url_trailer = models.URLField()
    description = models.TextField()
    video_type = models.CharField(max_length=5, choices=VIDEO_CHOISES)
    relise_date = models.DateField()
    age_limit = models.IntegerField()
    date = models.DateField()
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)


class Halls(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"


class Sessions(models.Model):

    id = models.AutoField(primary_key=True)
    hall_id = models.ForeignKey(Halls, on_delete=models.CASCADE)
    movie_id= models.ForeignKey(Movies, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_session = models.TimeField()
    duration = models.TimeField()
    date = models.DateField()

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеанси"

class Seats(models.Model):

    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    number_row = models.IntegerField()
    seat = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    class Meta:
        verbose_name = "Місце"
        verbose_name_plural = "Місця"


class Tickets(models.Model):

    STATUS_CHOICES = [
        ("S","Куплене"),
        ("F", "Вільне"),
        ("N", "Не доступно")
    ]

    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE, related_name="tickets", null= True)
    seat = models.ForeignKey(Seats, on_delete=models.CASCADE, related_name="tickets",null= True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="tickets", null= True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="F")
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Квиток"
        verbose_name_plural = "Квитки"

class Cinemas(models.Model):

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE)
    seo_url = models.SlugField(unique=True, blank=True, verbose_name="SEO URL")
    title = models.CharField(max_length = 255)
    description = models.TextField()
    conditions = models.TextField()
    halls_id = models.ForeignKey(Halls, on_delete= models.CASCADE)
    city = models.CharField(max_length=100)
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатри'