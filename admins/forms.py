from django import forms
from main.models import Block_SEO, Gallery, Picture, MainPaiges
from  movie.models import Movies
from  users.models import User
from core.models import Cinemas, Halls, Sessions,Seats, Tickets
from main.models import Banners, Cross_Banner, News, PaigesNews, Promotion, PaigesCinema, Contact
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django.forms.widgets import HiddenInput

class ContactForm(forms.ModelForm):
    contact_picture = forms.ImageField(required=False, label="Лого")
    delete_contact_picture = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = Contact
        fields = ['title', 'address', 'latitude', 'longitude', 'phone_number', 'gallery']
        widgets = {
            'longitude': HiddenInput(), # Теперь HiddenInput будет распознан
            'gallery': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['gallery'].required = False

        if self.instance and self.instance.pk:
            current_gallery = self.instance.gallery
            if current_gallery:
                first_picture = current_gallery.pictures.first()
                if first_picture:
                    self.current_contact_image = first_picture

    def clean_gallery(self):
        gallery_data = self.cleaned_data.get('gallery')
        if gallery_data is None:
            return None
        if isinstance(gallery_data, str) and not gallery_data:
            return None
        return gallery_data

    def save(self, commit=True):
        contact = super().save(commit=False)

        contact_picture = self.cleaned_data.get('contact_picture')
        delete_contact_picture = self.cleaned_data.get('delete_contact_picture')

        if delete_contact_picture:
            if contact.gallery:
                contact.gallery.delete()
                contact.gallery = None
        elif contact_picture:
            if contact.gallery:
                contact.gallery.pictures.all().delete()
                gallery = contact.gallery
            else:
                gallery = Gallery.objects.create()
                contact.gallery = gallery

            Picture.objects.create(gallery=gallery, image=contact_picture)
        elif not contact.gallery:
             contact.gallery = None

        if commit:
            contact.save()
        return contact

    def get_current_contact_image(self):
        if self.instance and self.instance.pk and self.instance.gallery:
            return self.instance.gallery.pictures.first()
        return None

# Важно: используйте modelformset_factory для Contact, так как Gallery - это ForeignKey на Contact
# А не inlineformset_factory, если вы не управляете Gallery как инлайн-дочерними объектами Contact.
ContactFormSet = modelformset_factory(Contact, form=ContactForm, extra=0, can_delete=True)


class MainPaigesForm(forms.ModelForm):
    class Meta:
        model = MainPaiges
        exclude = ['id', 'seo_block', ] # Убедитесь, что 'seo_block' действительно нужно исключать, если это связано с SEO_text
        # fields = '__all__' # Если вы используете exclude, то fields = '__all__' не нужен и может вызвать конфликт.
                           # Лучше перечислить все поля явно, если exclude вызывает проблемы, или убрать fields = '__all__'
        labels = {
            'phone_1': 'Телефон ',
            'phone_2': ' ',
            'SEO_text': 'SEO текст ',
        }

        widgets = {
            # Здесь вы уже добавляете 'form-control', но мы хотим добавить еще 'phone-input'
            'phone_1': forms.TextInput(attrs={'class': 'form-control phone-input'}), # Добавили phone-input
            'phone_2': forms.TextInput(attrs={'class': 'form-control phone-input'}), # Добавили phone-input

            'SEO_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'is_active': forms.CheckboxInput(attrs={'data-bootstrap-switch': ''}),
        }

    # Метод __init__ должен быть здесь, прямо внутри класса MainPaigesForm, но вне Meta
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].widget.attrs.update({'data-bootstrap-switch': 'true'}),


class PaigesCinemaForm(forms.ModelForm):
    class Meta:
        model = PaigesCinema
        exclude = ['id', 'seo_block', 'gallery']
        fields = '__all__'
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'data-bootstrap-switch': ''}),}


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

    image = forms.ImageField(label='')
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
        self.fields['gallery'].label = ''
        self.fields['image_type'].label = ''
        self.fields['image'].label = 'Главная картинка'

        self.fields['image'].widget.attrs.update({
            'style': 'display: none;',  # <-- повністю ховає стандартну кнопку
        })

        if 'id' in self.fields:
            self.fields['id'].label = ''

        if not self.instance.pk:
            self.initial['image_type'] = 'gallery'


PictureFormSet = modelformset_factory( model=Picture, form=PictureForm, fields=['image', 'gallery', 'image_type'],
                                                                                        extra=1,can_delete=True,)
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
        fields = ['title_seo', 'seo_url',   'seo_keywords', 'seo_description']
        labels = {
            "title_seo": 'title',
            "seo_url" : "URL ",
            "seo_keywords" : "keywords",

            'seo_description':'description'

        }
        widgets = {

            'seo_description': forms.Textarea(attrs={'class':'form-control'}),
            "title_seo":  forms.TextInput(attrs={'class':'form-control'}),
            "seo_url":  forms.TextInput(attrs={'class':'form-control'}),
            "seo_keywords":  forms.TextInput(attrs={'class':'form-control'}),


        }


class MovieForm(forms.ModelForm):

    class Meta:
        model = Movies

        fields = ['genre', 'title', 'url_trailer', 'description',
                    'relise_date', 'age_limit', 'is_2d','is_3d','is_imax']
        labels = {
            'genre': 'Жанр:',
            'title': 'Назва:',
            'url_trailer': 'URL трейлера:',
            'description': 'Опис:',

            'relise_date': 'Дата проката:',
            'age_limit': 'Вікова категорія:',
            'is_2d': ' 2D ',
            'is_3d': ' 3D ',
            'is_imax': ' IMAX ',
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'url_trailer': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'relise_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            'age_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_2d': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-bootstrap-switch': ''}),

            'is_3d': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-bootstrap-switch': ''}),

            'is_imax': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-bootstrap-switch': ''}),

        }



PICTURE_TYPE_DEFAULT = 'gallery'

PictureFormSet1 = inlineformset_factory( Gallery,  Picture, form=PictureForm,  fields=('image', 'image_type'),
                                                                    extra=1,    max_num=10,    can_delete=True,)





