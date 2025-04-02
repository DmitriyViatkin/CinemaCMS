from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Block_SEO(models.Model):
    id = models.AutoField(primary_key=True)
    title_seo = models.CharField(max_length=250)
    seo_url = models.SlugField()
    seo_text = models.TextField()
    seo_keywords = models.CharField(max_length=250)
    seo_description = models.TextField()


class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    image_type = models.CharField(max_length=20,
                                  choices=[('main_picture', 'Главное изображение'), ('gallery', 'Галерея')])
    image = models.ImageField(upload_to='images/')
    alter_txt = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Изображение для {self.content_object} ({self.image_type})"


class Baners(models.Model):
    id = models.AutoField(primary_key=True)
    picture = GenericRelation(Picture)
    url = models.URLField()
    text = models.CharField(max_length=100)
    scroll_speed = models.TimeField()
    type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)


class PaigesCinema(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE)
    picture = GenericRelation(Picture)
    description = models.TextField()
    date = models.DateField()
    is_active = models.BooleanField(default=False)


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    page_id = models.ForeignKey(PaigesCinema, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    latitude = models.FloatField()
    longitude= models.FloatField()
    phone_number = models.CharField(max_length=15)


class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE)
    picture = GenericRelation(Picture)
    description = models.TextField()
    url_video= models.URLField()
    date_publication = models.DateField()
