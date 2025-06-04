from django import forms
from main.models import Block_SEO, Gallery, Picture
from  movie.models import Movies
from  users.models import User
from core.models import Cinemas, Halls, Sessions,Seats, Tickets
from main.models import Banners, Cross_Banner, News, PaigesNews, Promotion, PaigesCinema
from django.forms import inlineformset_factory, formset_factory, modelformset_factory


class PaigesCinemaForm(forms.ModelForm):
    class Meta:
        model = PaigesCinema
        exclude = ['id', 'seo_block', 'gallery']
        fields = '__all__'
        widgets = {
            'is_active': forms.CheckboxInput(),}

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['title', 'description', 'url_video', 'date', 'is_active']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'is_active': forms.CheckboxInput()
        }

class PaigesNewsForm(forms.ModelForm):
    class Meta:
        model=PaigesNews
       # exclude =['id', 'seo_block', 'gallery']
        fields = ['title', 'description', 'url', 'date', 'is_active']
        widgets= {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'is_active':forms.CheckboxInput()
        }

class CrossBannerForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='Зображення для банера', widget=forms.FileInput() )
    type = forms.CharField(widget=forms.HiddenInput(), required=False, initial='photo_background')

    class Meta:
        model = Cross_Banner
        fields = ['type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.gallery:
            picture = self.instance.gallery.pictures.first()
            if picture and picture.image:
                self.fields['image'].initial = picture.image

    def save(self, commit=True):

        instance = super().save(commit=False)

        if commit:
            instance.save()
        return instance


class UserForm(forms.ModelForm):
    class Meta:
        model = User

        fields = '__all__'
        exclude = ['last_login', 'date_joined', 'groups', 'user_permissions', 'password']

class PictureForm(forms.ModelForm):

    image = forms.ImageField(label='Зображення')
    class Meta:
        model = Picture

        fields = ['image', 'gallery', 'image_type']

        widgets = {
            'gallery': forms.HiddenInput(),
            'image_type': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['gallery'].required = False
        self.fields['gallery'].label = ''  # Устанавливаем пустую метку
        self.fields['image_type'].label = ''  # Устанавливаем пустую метку


        if 'id' in self.fields:
            self.fields['id'].label = ''

        if not self.instance.pk:
            self.initial['image_type'] = 'gallery'

PictureFormSet = modelformset_factory(
    model=Picture,
    form=PictureForm,
    fields=['image', 'gallery', 'image_type'], # Поля должны совпадать с Meta.fields формы
    extra=1,
    can_delete=True,
)
class GalleryForm(forms.ModelForm):

    class Meta:
        model = Gallery
        fields = '__all__'
        widgets = {
            'scroll_speed': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
        }


class BannerForm(forms.ModelForm):
        main_picture = forms.ImageField(required=False, label='Головне зображення')

        class Meta:
            model = Banners
            fields = ['url', 'text', 'scroll_speed', 'is_active']

        def save(self, commit=True):
            banner = super().save(commit=False)
            # Якщо у банера немає галереї — створимо
            if not banner.gallery:
                gallery = Gallery.objects.create()
                banner.gallery = gallery
            if commit:
                banner.save()


                main_picture_file = self.cleaned_data.get('main_picture')
                if main_picture_file:

                    picture = banner.gallery.pictures.filter(image_type='main_picture').first()
                    if not picture:
                        picture = Picture(gallery=banner.gallery, image_type='main_picture')
                    picture.image = main_picture_file
                    picture.save()

            return banner

BannersFormSet = modelformset_factory(Banners, form=BannerForm, extra=0, can_delete=True)

class NewsForm(forms.ModelForm):
    main_picture = forms.ImageField(required=False, label='Головне зображення')

    class Meta:
        model = News
        fields = ['url', 'scroll_speed', 'is_active']

    def save(self, commit=True):
        news = super().save(commit=False)


        if not news.gallery:
            gallery = Gallery.objects.create()
            news.gallery = gallery

        if commit:
            news.save()


            main_picture_file = self.cleaned_data.get('main_picture')
            if main_picture_file:
                picture = news.gallery.pictures.filter(image_type='main_picture').first()
                if not picture:
                    picture = Picture(gallery=news.gallery, image_type='main_picture')
                picture.image = main_picture_file
                picture.save()

        return news

NewsFormSet = modelformset_factory(News, form=NewsForm, extra=0, can_delete=True)


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



PICTURE_TYPE_DEFAULT = 'gallery'

PictureFormSet1 = inlineformset_factory(
    Gallery,
    Picture,
    form=PictureForm,
    fields=('image', 'image_type'),
    extra=1,
    max_num=10,
    can_delete=True,
)





