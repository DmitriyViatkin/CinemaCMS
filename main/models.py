from django.db import models


class Block_SEO(models.Model):
    id = models.AutoField(primary_key=True)
    title_seo = models.CharField(max_length=250)
    seo_url = models.SlugField()
    seo_text = models.TextField()
    seo_keywords = models.CharField(max_length=250)
    seo_description = models.TextField()
    def __str__(self):
        return self.title_seo

    class Meta:
        verbose_name = 'Блок СЕО'
        verbose_name_plural = 'Бблоки СЕО'


class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    image_type = models.CharField(max_length=20,
                                  choices=[('main_picture', 'Главное изображение'), ('gallery', 'Галерея')])
    image = models.ImageField(upload_to='images/')
    alter_txt = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.get_image_type_display()} ({self.image.name})"
    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class Baners(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField()
    text = models.CharField(max_length=100)
    scroll_speed = models.TimeField()
    type = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Банер'
        verbose_name_plural = 'Банери'


class PaigesCinema(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE)
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сторінка'
        verbose_name_plural = 'Сторінки'


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    page_id = models.ForeignKey(PaigesCinema, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=250)
    latitude = models.FloatField()
    longitude= models.FloatField()
    phone_number = models.CharField(max_length=15)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакти'


class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE)
    picture = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    url_video= models.URLField()
    date_publication = models.DateField()
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Акція'
        verbose_name_plural = 'Акції'
