from django import forms
from main.models import Block_SEO, Gallery, Picture, MainPaiges
from  movie.models import Movies
from  users.models import User, Email_campaing, Tamplate_email
from core.models import Cinemas, Halls, Sessions,Seats, Tickets
from main.models import Banners, Cross_Banner, News, PaigesNews, Promotion, PaigesCinema, Contact
from django.forms import inlineformset_factory, formset_factory, modelformset_factory
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _


class TemplateEmailForm(forms.ModelForm):

    class Meta:
        model = Tamplate_email
        fields = ['template_file']
        labels = {
            'template_file': "Загрузить файл шаблона (HTML, TXT и т.д.)",
        }



class EmailSendForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(email__isnull=False).exclude(email=""),
        widget=forms.CheckboxSelectMultiple,
        label="Одержувачі"
    )

    html_file = forms.FileField(label="HTML шаблон листа (файл)", required=True)

    def clean_html_file(self):
        html_file = self.cleaned_data.get("html_file")
        if html_file and not html_file.name.endswith('.html'):
            raise forms.ValidationError("Файл повинен мати розширення .html")
        return html_file

class SellectUserForm(forms.ModelForm):

        class Meta:
            model = Email_campaing
            fields = ['users']

            widgets = {
                'users': forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}),
            }

            labels = {
                  'users': 'Выберите пользователей для кампании',
              }


class EmailCampaignForm(forms.ModelForm):

    users = forms.CharField(
        required=False,
        widget=forms.HiddenInput,
        help_text="Список ID пользователей, разделенных запятыми."
    )

    recipient_mode = forms.ChoiceField(
        choices=[
            ('all', 'Всі користувачі'),
            ('selected', 'Вибірково'),
        ],
        widget=forms.RadioSelect,
        initial='all',
        label='Виберіть отримувачів розсилки'
    )

    new_template_file = forms.FileField(
        label="Загрузить НОВЫЙ файл шаблона (HTML, TXT и т.д.)",
        required=False,
        help_text="Загрузите файл для нового шаблона Email. Если выбрано, этот шаблон будет связан с кампанией."
    )

    class Meta:
        model = Email_campaing
        fields = ['new_template_file', 'template', 'status', 'users']
        labels = {
            'status': "Статус кампании",
            'template': "Выбрать существующий шаблон Email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = Tamplate_email.objects.order_by('-id')

        if not self.instance.pk:
            self.fields['recipient_mode'].initial = 'all'
        elif self.instance.users.exists():
            self.fields['recipient_mode'].initial = 'selected'

            initial_user_ids = list(self.instance.users.values_list('id', flat=True))
            self.initial['users'] = ','.join(map(str, initial_user_ids))
        else:
            self.fields['recipient_mode'].initial = 'all'


    def clean_users(self):
        users_str = self.cleaned_data.get('users', '')
        recipient_mode = self.data.get('recipient_mode')
        if recipient_mode == 'all':
            return []


        if users_str:
            try:
                user_ids = [int(uid.strip()) for uid in users_str.split(',') if uid.strip()]
            except ValueError:
                raise forms.ValidationError("Неверный формат ID пользователя. Ожидается список чисел через запятую.")


            existing_user_ids = User.objects.filter(id__in=user_ids).values_list('id', flat=True)
            if len(set(user_ids)) != len(existing_user_ids):
                invalid_ids = set(user_ids) - set(existing_user_ids)
                raise forms.ValidationError(f"Некоторые выбранные ID пользователей недействительны или не существуют: {list(invalid_ids)}")

            return user_ids
        else:

            raise forms.ValidationError("Виберіть хоча б одного користувача для розсилки.")

    def clean(self):
        cleaned_data = super().clean()
        existing_template = cleaned_data.get('template')
        new_template_file = cleaned_data.get('new_template_file')

        if not existing_template and not new_template_file:
            self.add_error(None, "Пожалуйста, выберите существующий шаблон ИЛИ загрузите новый файл шаблона.")
        elif existing_template and new_template_file:
            self.add_error(None, "Нельзя выбрать существующий шаблон И загрузить новый одновременно. Пожалуйста, выберите что-то одно.")

        return cleaned_data

class ContactForm(forms.ModelForm):
    contact_picture = forms.ImageField(required=False, label="Лого")
    delete_contact_picture = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput())

    class Meta:
        model = Contact
        fields = ['title', 'address', 'latitude', 'longitude', 'phone_number',]
        widgets = {
            'longitude': HiddenInput(),
            'gallery': HiddenInput(),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'cols': '50', 'rows': '10', 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control phone-input'}),
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


ContactFormSet = modelformset_factory(Contact, form=ContactForm, extra=0, can_delete=True)


class MainPaigesForm(forms.ModelForm):
    class Meta:
        model = MainPaiges
        exclude = ['id', 'seo_block', ]
        labels = {
            'phone_1': 'Телефон ',
            'phone_2': ' ',
            'SEO_text': 'SEO текст ',
        }

        widgets = {

            'phone_1': forms.TextInput(attrs={'class': 'form-control phone-input'}),
            'phone_2': forms.TextInput(attrs={'class': 'form-control phone-input'}),

            'SEO_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'is_active': forms.CheckboxInput(attrs={'data-bootstrap-switch': ''}),
        }


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
        labels = {
            'title':"Назва Акції",
            'description':"Опис",
            'url_video': "Посилання на відео",
            'date':"Дата публікації",
            'is_active':"Вкл"
        }
        widgets = {
            'title': forms.TextInput(attrs={ 'class': 'form-control'}),
            'description': forms.Textarea(attrs={  'cols': '50', 'rows': '10','class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date','class': 'form-control float-right'}),
            'is_active': forms.CheckboxInput(),
            'url_video':forms.URLInput(attrs={'size': '30',"class":"form-control float-right"})
        }


class PaigesNewsForm(forms.ModelForm):
    class Meta:
        model=PaigesNews

        fields = ['title', 'description', 'url', 'date', 'is_active']
        labels = {
            'title': _("Назва новини"),
            'description': _("Опис"),
            'url': _("Посилання на відео"),
            'date': _("Дата публікації"),
            'is_active': _("Вкл")
        }
        widgets = {
            'title': forms.TextInput(attrs={'size': '30', 'class': 'form-control float-center'}),
            'description': forms.Textarea(attrs={'cols': '50', 'rows': '10', 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control float-right'}),
            'is_active': forms.CheckboxInput(),
            'url': forms.URLInput(attrs={'size': '30', "class": "form-control float-right"})
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
            'style': 'display: none;',
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

        fields = [ 'title', 'cinema', 'scheme_hall','description',  ]
        labels = {

            'title':_('Назва'),
            'cinema':_('Кінотеатр'),
            'scheme_hall':_('Схема залу'),
            'description':_("Опис"),

        }

class CinemaForm(forms.ModelForm):

    class Meta:
        model = Cinemas

        fields = ['title', 'description' , 'conditions', 'city',]
        widgets = {

            'description': forms.Textarea(attrs={'class': 'form-control'}),
            "conditions": forms.Textarea(attrs={'class': 'form-control'}),
            "seo_url": forms.URLInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),

        }


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
            'genre': _('Жанр:'),
            'title': _('Назва:'),
            'url_trailer': _('URL трейлера:'),
            'description': _('Опис:'),

            'relise_date': _('Дата проката:'),
            'age_limit': _('Вікова категорія:'),
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





