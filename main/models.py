from django.db import models


class Block_SEO(models.Model):
    id = models.AutoField(primary_key=True)
    title_seo = models.CharField(max_length=250, verbose_name= 'Заголовок')
    seo_url = models.SlugField(verbose_name= 'URL адреса ')
    seo_text = models.TextField(verbose_name= 'текст')
    seo_keywords = models.CharField(max_length=250, verbose_name= 'Ключові слова')
    seo_description = models.TextField(verbose_name= 'Опис')
    def __str__(self):
        return self.title_seo

    class Meta:
        verbose_name = 'Блок СЕО'
        verbose_name_plural = 'Блоки СЕО'

class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250, verbose_name= 'Фильм')
    image_type = models.CharField(max_length=20,
                                  choices=[('main_picture', 'Главное изображение'), ('gallery', 'Галерея')],
                                  verbose_name='Тип зображення')
    image = models.ImageField(upload_to='images/', verbose_name='Зображення')
    alter_txt = models.CharField(max_length=255, blank=True, null=True, verbose_name='Альтернативний текст')

    def __str__(self):
        return f'{self.title} {self.image_type} '

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'

class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    picture = models.ManyToManyField(Picture, related_name='galleries', verbose_name='Зображення')




    class Meta:
        verbose_name = 'Галерея'
        verbose_name_plural = 'Галереї'



class Baners(models.Model):
    id = models.AutoField(primary_key=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    url = models.URLField(verbose_name= 'URL адреса ')
    text = models.CharField(max_length=100,verbose_name= 'текст')
    scroll_speed = models.TimeField(verbose_name= 'Швидкість прокрутки')
    type = models.CharField(max_length=100,verbose_name= 'ТИп')
    is_active = models.BooleanField(default=False,verbose_name= 'Показувати ')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Банер'
        verbose_name_plural = 'Банери'


class PaigesCinema(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    description = models.TextField(verbose_name= 'Опис')
    date = models.DateField()
    is_active = models.BooleanField(default=False, verbose_name= 'Показ')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сторінка'
        verbose_name_plural = 'Сторінки'


class Contact(models.Model):
    id = models.AutoField(primary_key=True)

    title = models.CharField(max_length=100, verbose_name= 'Опис ')
    address = models.CharField(max_length=250, verbose_name= 'Адреса ')
    latitude = models.FloatField(verbose_name= 'Довгота ')
    longitude= models.FloatField(verbose_name= 'Широта ')
    phone_number = models.CharField(max_length=15, verbose_name= 'Номер телефону')
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакти'


class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name= 'Блок СЕО ')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    description = models.TextField(verbose_name= 'Опис')
    url_video= models.URLField(verbose_name= 'URL адреса ')
    date_publication = models.DateField(verbose_name= 'Дата ')
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Акція'
        verbose_name_plural = 'Акції'
