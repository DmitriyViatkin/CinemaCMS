from django import forms
from main.models import Block_SEO, Gallery, Picture
from  movie.models import Movies
from core.models import Cinemas, Halls, Sessions
from django.forms import inlineformset_factory



class SessionsForm(forms.ModelForm):
    class Meta:
        model = Sessions

        fields = ['cinema', 'hall_id', 'movie', 'title', 'time_session','duration','date' ]



class HallsForm(forms.ModelForm):
    class Meta:
        model = Halls
        exclude = ['date', 'gallery']
        fields = ['seo_block', 'title', 'cinema', 'description',  ]


class CinemaForm(forms.ModelForm):

    class Meta:
        model = Cinemas

        fields = ['title', 'description' , 'conditions', 'city',]



class BlockSEOForm(forms.ModelForm):

    class Meta:
        model = Block_SEO
        fields = ['title_seo', 'seo_url', 'seo_text', 'seo_keywords', 'seo_description']
        widgets = {
            'seo_text': forms.Textarea(attrs={'rows': 4}),
            'seo_description': forms.Textarea(attrs={'rows': 4}),
        }

class MovieForm(forms.ModelForm):

    class Meta:
        model = Movies

        fields = ['genre', 'title', 'url_trailer', 'description',
                  'video_type', 'relise_date', 'age_limit']

        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'relise_date': forms.DateInput(attrs={'type': 'date'}),
        }


PictureFormSet = inlineformset_factory(
    Gallery,       # Батьківська модель
    Picture,       # Дочірня модель
    fields=('image_type', 'image', 'alter_txt'), # Користувач обирає тип для кожної картинки
    extra=4,
    max_num=10,
    can_delete=True
)
class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title'] # Включаємо поле 'title'

# Ваш PictureFormSet залишається таким, як є:
from django.forms import inlineformset_factory