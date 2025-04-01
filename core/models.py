from django.db import models
from users.models import Profile
from main.models import Block_SEO, Picture
from django.contrib.contenttypes.fields import GenericRelation






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
    picture = GenericRelation(Picture)


class Halls(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    seats_id = models.ForeignKey(Seats, on_delete=models.CASCADE)
    description = models.TextField()
    picture = GenericRelation(Picture)
    date = models.DateField()


class Sessions(models.Model):

    id = models.AutoField(primary_key=True)
    hall_id = models.ForeignKey(Halls, on_delete=models.CASCADE)
    movie_id= models.ForeignKey(Movies, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_session = models.TimeField()
    duration = models.TimeField()
    date = models.DateField

class Seats(models.Model):

    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    number_row = models.IntegerField()
    seat = models.IntegerField()
    date = models.DateField()


class Tickets(models.Model):

    STATUS_CHOISES = {
        "S":"Куплене",
        "F": "Вільне",
        "N": "Не доступно"
    }

    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(Sessions)
    seats_id = models.ForeignKey(Seats)
    profile_id = models.ForeignKey(Profile)
    status = models.CharField(max_length=12, choices=STATUS_CHOISES)


class Cinemas(models.Model):

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE)
    title = models.CharField(max_length = 255)
    description = models.TextField()
    conditions = models.TextField()
    halls_id = models.ForeignKey(Halls, on_delete= models.CASCADE)
    city = models.CharField(max_length=100)
    picture = GenericRelation(Picture)
    date = models.DateField()