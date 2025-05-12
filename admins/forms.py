from django import forms
from main.models import Block_SEO, Gallery, Picture
from  movie.models import Movies
from  users.models import User
from core.models import Cinemas, Halls, Sessions,Seats, Tickets
from main.models import Banners
from django.forms import inlineformset_factory, formset_factory, modelformset_factory


class UserForm(forms.ModelForm):
    class Meta:
        model = User

        fields = '__all__'
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions', 'password']

class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture

        fields = ['image_type', 'image',]
        widgets = {

            'image_type': forms.Select(attrs={'class': 'form-control'}),


        }
        labels = {

            'image_type': 'Тип зображення',
            'image': 'Зображення',


        }
class GalleryForm(forms.ModelForm):
    class Meta:
        model = Gallery
        fields = ['title']

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banners
        exclude = ['gallery']
        fields=['url', 'text', 'scroll_speed', 'type', 'is_active']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),

                    }
        labels = {
            'URL': 'URL',
            'text': 'Текст',
            'scroll_speed': 'Скорость прокрутки',
            'type': 'Тип',
            'is_active': 'Показувати', }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Tickets

        fields = ['session', 'movie', 'seat', 'profile', 'halls']
        widgets = {
            'session': forms.Select(attrs={'class': 'form-control'}),
            'movie': forms.Select(attrs={'class': 'form-control'}),
            'seat': forms.Select(attrs={'class': 'form-control'}),
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'halls': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'session': 'Сеанс',
            'movie': 'Фільм',
            'seat': 'Місце',
            'profile': 'Глядач',
            'halls': 'Зал',}


class SeatForm(forms.ModelForm):
    class Meta:
        model = Seats
        fields = ['number_row', 'halls','seat', 'status', 'is_vip', 'price']


class SessionsForm(forms.ModelForm):
    class Meta:
        model = Sessions
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_session': forms.TimeInput(attrs={'type': 'time'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
        }

SessionFormSet = modelformset_factory(Sessions, form=SessionsForm, fields='__all__', extra=1)


class HallsForm(forms.ModelForm):
    class Meta:
        model = Halls

        exclude = ['seo_block','date', 'gallery']

        fields = [ 'title', 'cinema', 'description', 'rows', 'seats_row']


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
    Gallery,
    Picture,
    fields=('image_type', 'image',),
    extra=1,
    max_num=10,
    can_delete=True
)


BannersFormSet = inlineformset_factory(
    Gallery, Banners, form=BannerForm,
    extra=1, can_delete=True
)



