from django import forms
from main.models import Block_SEO, Gallery, Picture
from  movie.models import Movies
from  users.models import User
from core.models import Cinemas, Halls, Sessions,Seats, Tickets
from main.models import Banners, Cross_Banner
from django.forms import inlineformset_factory, formset_factory, modelformset_factory


class CrossBannerForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='Зображення для банера')
    image_type = forms.CharField(widget=forms.HiddenInput(), initial='gallery')

    gallery = forms.ModelChoiceField(queryset=Gallery.objects.all(), widget=forms.HiddenInput(), required=False)
    type = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Cross_Banner
        fields = ['gallery', 'type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            last_id = Gallery.objects.order_by('-id').first()
            self.initial['gallery'] = (last_id.id + 1) if last_id else 1

    def save(self, commit=True):
        self.instance.gallery = Gallery.objects.create()
        self.instance.type = self.cleaned_data['banner_type_choice']
        cross_banner = super().save(commit)

        image = self.cleaned_data.get('image')
        if image:
            Picture.objects.create(
                gallery=self.instance.gallery,
                image=image,
                image_type=self.cleaned_data['image_type']
            )
        return cross_banner


class UserForm(forms.ModelForm):
    class Meta:
        model = User

        fields = '__all__'
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions', 'password']

class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['image']
        widgets = {
            'image': forms.FileInput(),
        }
        labels = {
            'image': 'Зображення',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'image_type' in self.initial:
            self.instance.image_type = self.initial['image_type']


class GalleryForm(forms.ModelForm):

    class Meta:
        model = Gallery
        fields = '__all__'
        widgets = {
            'scroll_speed': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
        }


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banners
        exclude = ['gallery', 'type']
        fields = ['url', 'text', 'scroll_speed', 'is_active']
        widgets = {
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'scroll_speed': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'url': 'URL',
            'text': 'Текст',
            'scroll_speed': 'Швидкість прокрутки (сек.)',
            'is_active': 'Показувати',
        }

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


PictureFormSet1 = inlineformset_factory(
    Gallery,
    Picture,
    form=PictureForm,
    fields=('image_type', 'image',),
    extra=0,
    max_num=10,
    can_delete=True )

PICTURE_TYPE_DEFAULT = 'gallery'  # Замініть на потрібне значення за замовчуванням

PictureFormSet = inlineformset_factory(
    Gallery,
    Picture,
    form=PictureForm,
    fields=('image',),  # Тепер включаємо лише 'image'
    extra=0,
    max_num=10,
    can_delete=True,)

BannerFormSet = modelformset_factory(
    Banners,
    form=BannerForm,
    extra=1,  # Кількість порожніх форм для відображення
    exclude=['gallery', 'type']
)


class CombinedBannerPictureForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    url = forms.URLField(label='URL', widget=forms.URLInput(attrs={'class': 'form-control'}), required=False)
    text = forms.CharField(label='Текст', widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    scroll_speed = forms.IntegerField(label='Скорость прокрутки (сек.)', widget=forms.NumberInput(attrs={
        'class': 'form-control'}), required=False)
    is_active = forms.BooleanField(label='Показывать', widget=forms.CheckboxInput(attrs={
        'class': 'form-control'}), required=False)
    image = forms.ImageField(label='Изображение', widget=forms.FileInput(attrs={
        'class': 'form-control-file'}), required=False)
    image_type = forms.ChoiceField(
        label='Тип изображения',
        choices=Picture.objects.none().model.image_type.field.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'image_type' in self.initial:
            self.fields['image_type'].initial = self.initial['image_type']

class CombinedNewsPictureForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    url = forms.URLField(label='URL', widget=forms.URLInput(attrs={'class': 'form-control'}), required=False)
    text = forms.CharField(label='Текст', widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    scroll_speed = forms.IntegerField(label='Скорость прокрутки (сек.)', widget=forms.NumberInput(attrs={
        'class': 'form-control'}), required=False)
    is_active = forms.BooleanField(label='Показывать', widget=forms.CheckboxInput(attrs={
        'class': 'form-control'}), required=False)
    image = forms.ImageField(label='Изображение', widget=forms.FileInput(attrs={
        'class': 'form-control-file'}), required=False)
    image_type = forms.ChoiceField(
        label='Тип изображения',
        choices=Picture.objects.none().model.image_type.field.choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'image_type' in self.initial:
            self.fields['image_type'].initial = self.initial['image_type']