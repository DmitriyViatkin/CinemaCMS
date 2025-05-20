from django.db import models


class Block_SEO(models.Model):
    id = models.AutoField(primary_key=True)
    title_seo = models.CharField(max_length=250, verbose_name= 'Заголовок') # Залишаємо обов'язковим
    seo_url = models.SlugField(verbose_name= 'URL адреса ', unique=True) # Додали unique=True раніше, за замовчуванням обов'язкове
    seo_text = models.TextField(verbose_name= 'текст', blank=True) # <--- ЗРОБЛЕНО НЕОБОВ'ЯЗКОВИМ
    seo_keywords = models.CharField(max_length=250, verbose_name= 'Ключові слова', blank=True) # <--- ЗРОБЛЕНО НЕОБОВ'ЯЗКОВИМ
    seo_description = models.TextField(verbose_name= 'Опис', blank=True) # <--- ЗРОБЛЕНО НЕОБОВ'ЯЗКОВИМ



    def __str__(self):
        return self.seo_url # Або title_seo

    class Meta:
        verbose_name = 'Блок СЕО'
        verbose_name_plural = 'Блоки СЕО'

class Gallery(models.Model):
    id = models.AutoField(primary_key=True)


    class Meta:
        verbose_name = 'Галерея'
        verbose_name_plural = 'Галереї'




class Picture(models.Model):
    id = models.AutoField(primary_key=True)
    gallery = models.ForeignKey(Gallery, related_name='pictures', on_delete=models.CASCADE, verbose_name='Галерея')
    image_type = models.CharField(max_length=20, choices=[('main_picture', 'Главное изображение'), ('gallery', 'Галерея')],
        verbose_name='Тип зображення')
    image = models.ImageField(upload_to='images/', verbose_name='Зображення')


    def __str__(self):
        return self.image_type

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class Banners(models.Model):
    id = models.AutoField(primary_key=True)
    gallery = models.ForeignKey(
        Gallery,
        related_name='banners',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Картинка'
    )
    url = models.URLField(verbose_name='URL адреса')
    text = models.CharField(max_length=100, verbose_name='текст')
    scroll_speed = models.DurationField(verbose_name='Швидкість прокрутки (сек.)', null=True, blank=True)
    type = models.CharField(
        max_length=100,
        choices=[('baner_top', 'Сквозной банер'), ('news', 'новости')],
        default='baner_top',
        verbose_name='Тип'
    )
    is_active = models.BooleanField(default=False, verbose_name='Показувати')

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'Банер'
        verbose_name_plural = 'Банери'

class Cross_Banner (models.Model):
    id = models.AutoField(primary_key=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, null=True, blank=True, verbose_name= 'Картинка')
    type = models.CharField(choices=[('photo_background','фото на фоне'),('photo','просто фото')])
    TYPE_CHOICES = [
        ('photo_background', 'Фото на фоне'),
        ('photo', 'Просто фото'),
        # Додай сюди інші свої варіанти
    ]

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'Сквозной Банер'
        verbose_name_plural = 'Сквозние Банери'

class PaigesNews(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250, verbose_name='Назва')
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    description = models.TextField(verbose_name= 'Опис')
    url = models.URLField(verbose_name='URL адреса ')
    date = models.DateField()
    is_active = models.BooleanField(default=False, verbose_name= 'Показ')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сторінка Новини'
        verbose_name_plural = 'Сторінки Новин'

class MainPaiges (models.Model):
    name_cinema = models.CharField(max_length=250, verbose_name= "Кинотеатр")
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    SEO_text  = models.TextField(verbose_name= 'Сео текст ')
    phone = models.CharField(max_length=16, verbose_name= "Телефон")
    is_active = models.BooleanField(default=False, verbose_name= 'Показ')

    def __str__(self):
        return self.name_cinema

    class Meta:
        verbose_name = 'Головна сторінка'
        verbose_name_plural = 'Головні сторінки'

class PaigesCinema(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    title = models.CharField(max_length=250, verbose_name='Назва')
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
    title = models.CharField(max_length=100, verbose_name='Опис ')
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
