from django import forms
from main.models import Block_SEO, Gallery, Picture
from  movie.models import Movies
from core.models import Cinemas, Halls, Sessions,Seats, Tickets
from django.forms import inlineformset_factory

class TicketForm(forms.ModelForm):
    class Meta:
        model = Tickets
        # Включаємо поле 'movie' у список полів форми
        fields = ['session', 'movie', 'seat', 'profile', 'halls']
        widgets = {
            'session': forms.Select(attrs={'class': 'form-control'}),
            'movie': forms.Select(attrs={'class': 'form-control'}), # Це поле тепер включено у fields
            'seat': forms.Select(attrs={'class': 'form-control'}),
            'profile': forms.Select(attrs={'class': 'form-control'}),
            'halls': forms.Select(attrs={'class': 'form-control'}), # Примітка: це поле може бути надлишковим
        }
        labels = {
            'session': 'Сеанс',
            'movie': 'Фільм', # Виправлено друкарську помилку
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

        fields = ['cinema', 'hall_id', 'movie', 'time_session','duration','date' ]



class HallsForm(forms.ModelForm):
    class Meta:
        model = Halls
        # Исключаем только поля, которые не должны редактироваться вручную
        exclude = ['seo_block','date', 'gallery']
        # Указываем все редактируемые поля
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