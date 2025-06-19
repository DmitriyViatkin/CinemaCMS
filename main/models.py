from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Block_SEO(models.Model):
    id = models.AutoField(primary_key=True)
    title_seo = models.CharField(max_length=250, verbose_name= 'Заголовок')
    seo_url = models.SlugField(verbose_name= 'URL адреса ', unique=True)

    seo_keywords = models.CharField(max_length=250, verbose_name= 'Ключові слова', blank=True)
    seo_description = models.TextField(verbose_name= 'Опис', blank=True)



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
    image_type = models.CharField(max_length=20, choices=[('main_picture', 'Главное изображение'), ('gallery', 'Галерея'),
                                                          ('logo', 'Лого')],
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
    url = models.URLField(verbose_name='URL адреса', null=True, blank=True)
    text = models.CharField(max_length=100, verbose_name='текст', null=True, blank=True)
    scroll_speed = models.DurationField(verbose_name='Швидкість прокрутки (сек.)', null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name='Показувати')

    @property
    def image(self):

        if self.gallery:

            first_picture = self.gallery.pictures.first()
            if first_picture:
                return first_picture.image
        return None

    def __str__(self):
        return f"Банер {self.id}" + (f": {self.text[:50]}..." if self.text else "")

    class Meta:
        verbose_name = 'Банер'
        verbose_name_plural = 'Банери'


class News(models.Model):
    id = models.AutoField(primary_key=True)
    gallery = models.ForeignKey(
        Gallery,
        related_name='news',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Картинка'
    )
    url = models.URLField(verbose_name='URL адреса', null=True, blank=True)

    scroll_speed = models.DurationField(verbose_name='Швидкість прокрутки (сек.)', null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name='Показувати')

    @property
    def image(self):

        if self.gallery:

            first_picture = self.gallery.pictures.filter(image_type='gallery').first()
            if first_picture:
                return first_picture.image
        return None

    def __str__(self):

        return f"Новина {self.id}"


    class Meta:
        verbose_name = 'Новина'
        verbose_name_plural = 'Новини'


class Cross_Banner (models.Model):
    id = models.AutoField(primary_key=True)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, null=True, blank=True, verbose_name= 'Картинка')
    type = models.CharField(choices=[('photo_background','фото на фоне'),('photo','просто фото')])
    TYPE_CHOICES = [
        ('photo_background', 'Фото на фоне'),
        ('photo', 'Просто фото'),

    ]

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = 'Сквозной Банер'
        verbose_name_plural = 'Сквозние Банери'


class PaigesNews(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250, verbose_name=_('Назва'))
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= 'Картинка')
    description = models.TextField(verbose_name= _('Опис'))
    url = models.URLField(verbose_name=_('URL адреса '))
    date = models.DateField(default=timezone.localdate, verbose_name=_('Дата публікації'))


    is_active = models.BooleanField(default=False, verbose_name= _('Показ'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сторінка Новини'
        verbose_name_plural = 'Сторінки Новин'


class MainPaiges (models.Model):

    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    SEO_text  = models.TextField(verbose_name= _('СЕО текст '))
    phone_1  = models.CharField(max_length=16, verbose_name= _("Телефон"))
    phone_2 = models.CharField(max_length=16, verbose_name=_("Телефон"))
    is_active = models.BooleanField(default=False, verbose_name= _('Показ'))



    class Meta:
        verbose_name = 'Головна сторінка'
        verbose_name_plural = 'Головні сторінки'

class PaigesCinema(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.OneToOneField(Block_SEO, on_delete= models.CASCADE, verbose_name= 'Блок СЕО ')
    title = models.CharField(max_length=250, verbose_name=_('Назва'))
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= _('Картинка'))
    description = models.TextField(verbose_name= _('Опис'))
    date = models.DateField()
    is_active = models.BooleanField(default=False, verbose_name= _('Показ'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Сторінка'
        verbose_name_plural = 'Сторінки'


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    seo_block = models.ForeignKey(Block_SEO, on_delete=models.CASCADE, verbose_name='Блок СЕО ')
    gallery = models.ForeignKey(
        Gallery,
        related_name='contact',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Картинка'
    )
    title = models.CharField(max_length=100, verbose_name= 'Опис ')
    address = models.CharField(max_length=250, verbose_name= 'Адреса ')
    latitude = models.FloatField(null=True, blank=True, verbose_name='Довгота ')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Широта ')
    phone_number = models.CharField(max_length=15, verbose_name= 'Номер телефону')
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакти'

class Promotion(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, verbose_name=_('Опис '))
    seo_block = models.OneToOneField(Block_SEO, on_delete=models.CASCADE, verbose_name= 'Блок СЕО ')
    gallery = models.ForeignKey(Gallery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name= _('Картинка'))
    description = models.TextField(verbose_name= _('Опис'))
    url_video= models.URLField(verbose_name= 'URL адреса ')
    date = models.DateField(default=timezone.localdate, verbose_name=_('Дата публікації'))
    is_active = models.BooleanField(default=False, verbose_name=_('Показ'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Акція'
        verbose_name_plural = 'Акції'
