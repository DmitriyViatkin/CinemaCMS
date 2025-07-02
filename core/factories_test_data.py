import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from core.models import Cinemas, Halls, Sessions, Seats, Tickets
from main.models import Block_SEO, Gallery, Picture, Banners, News, Cross_Banner, PaigesNews, MainPaiges, PaigesCinema, Contact, Promotion
from movie.models import Movies
from users.models import User, Email_campaing, Tamplate_email

# ===================
# Общие фабрики
# ===================
class BlockSEOFactory(DjangoModelFactory):
    class Meta:
        model = Block_SEO

    title_seo  = factory.Faker('sentence')

    seo_url = factory.Faker('slug')

    seo_keywords  = factory.Faker('sentence', nb_words=3)

    seo_description = factory.Faker('paragraph')


class GalleryFactory(DjangoModelFactory):
    class Meta:
        model = Gallery


class PictureFactory(DjangoModelFactory):
    class Meta:
        model = Picture

    gallery = factory.SubFactory(GalleryFactory)
    image_type = factory.Iterator([('main_picture', 'main_picture'), ('gallery', 'gallery'), ('logo', 'logo')])
    image = factory.django.ImageField(color='blue')


# ===================
# Пользователи
# ===================
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    city = factory.Faker('city')
    address = factory.Faker('address')
    phone_number = factory.Faker('phone_number')
    gender = factory.Iterator(['man', 'women'])
    languages = factory.Iterator(['ru', 'ua'])  # предпочтительный язык
    date_of_birth = factory.Faker('date_of_birth')


# ===================
# Основной контент
# ===================
class CinemasFactory(DjangoModelFactory):
    class Meta:
        model = Cinemas

    seo_block = factory.SubFactory(BlockSEOFactory)

    title  = factory.Faker('company')

    description  = factory.Faker('paragraph')
    conditions  = factory.Faker('paragraph')

    city = factory.Faker('city')
    gallery = factory.SubFactory(GalleryFactory)


class HallsFactory(DjangoModelFactory):
    class Meta:
        model = Halls

    seo_block = factory.SubFactory(BlockSEOFactory)

    title   = factory.Faker('word')
    description  = factory.Faker('paragraph')

    cinema = factory.SubFactory(CinemasFactory)
    gallery = factory.SubFactory(GalleryFactory)
    scheme_hall = factory.django.FileField(filename='scheme_hall/example.json')


class MoviesFactory(DjangoModelFactory):
    class Meta:
        model = Movies

    seo_block = factory.SubFactory(BlockSEOFactory)

    title  = factory.Faker('sentence')

    description = factory.Faker('paragraph')
    genre = factory.Iterator(["DR", "COM", "ACT"])
    url_trailer = factory.Faker('url')
    relise_date = factory.Faker('date')
    age_limit = factory.Faker('pyint', min_value=0, max_value=18)
    is_2d = True
    is_3d = False
    is_imax = False
    gallery = factory.SubFactory(GalleryFactory)


class SessionsFactory(DjangoModelFactory):
    class Meta:
        model = Sessions

    cinema = factory.SubFactory(CinemasFactory)
    hall_id = factory.SubFactory(HallsFactory)
    movie = factory.SubFactory(MoviesFactory)
    time_session = timezone.now().time()
    duration = timezone.now().time()
    date = timezone.now().date()


class SeatsFactory(DjangoModelFactory):
    class Meta:
        model = Seats

    halls = factory.SubFactory(HallsFactory)
    number_row = factory.Faker('pyint', min_value=1, max_value=10)
    seat = factory.Faker('pyint', min_value=1, max_value=20)
    status = factory.Iterator(["F", "S", "N"])
    is_vip = factory.Faker('pybool')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)


class TicketFactory(DjangoModelFactory):
    class Meta:
        model = Tickets

    session = factory.SubFactory(SessionsFactory)
    movie = factory.SubFactory(MoviesFactory)
    seat = factory.SubFactory(SeatsFactory)
    profile = factory.SubFactory(UserFactory)
    halls = factory.SubFactory(HallsFactory)


# ===================
# Остальные модели с текстами
# ===================
class PaigesNewsFactory(DjangoModelFactory):
    class Meta:
        model = PaigesNews

    seo_block = factory.SubFactory(BlockSEOFactory)

    title  = factory.Faker('sentence')

    description  = factory.Faker('paragraph')
    url = factory.Faker('url')
    date = factory.Faker('date')
    gallery = factory.SubFactory(GalleryFactory)


class MainPaigesFactory(DjangoModelFactory):
    class Meta:
        model = MainPaiges

    seo_block = factory.SubFactory(BlockSEOFactory)

    SEO_text  = factory.Faker('paragraph')
    phone_1 = factory.Faker('phone_number')
    phone_2 = factory.Faker('phone_number')
    is_active = factory.Faker('pybool')


class PaigesCinemaFactory(DjangoModelFactory):
    class Meta:
        model = PaigesCinema

    seo_block = factory.SubFactory(BlockSEOFactory)

    title = factory.Faker('sentence')
    description = factory.Faker('paragraph')
    description = factory.Faker('paragraph')
    date = factory.Faker('date')
    gallery = factory.SubFactory(GalleryFactory)
    is_active = factory.Faker('pybool')


class ContactFactory(DjangoModelFactory):
    class Meta:
        model = Contact

    seo_block = factory.SubFactory(BlockSEOFactory)

    title  = factory.Faker('sentence')

    address  = factory.Faker('address')
    phone_number = factory.Faker('phone_number')
    latitude = factory.Faker('pyfloat')
    longitude = factory.Faker('pyfloat')
    gallery = factory.SubFactory(GalleryFactory)


class PromotionFactory(DjangoModelFactory):
    class Meta:
        model = Promotion

    seo_block = factory.SubFactory(BlockSEOFactory)

    title = factory.Faker('sentence')
    description  = factory.Faker('paragraph')

    url_video = factory.Faker('url')
    date = factory.Faker('date')
    gallery = factory.SubFactory(GalleryFactory)
    is_active = factory.Faker('pybool')


# ===================
# Баннеры и новости
# ===================
class BannerFactory(DjangoModelFactory):
    class Meta:
        model = Banners

    gallery = factory.SubFactory(GalleryFactory)
    url = factory.Faker('url')

    text = factory.Faker('sentence')
    is_active = factory.Faker('pybool')
    scroll_speed = timezone.timedelta(seconds=10)


class NewsFactory(DjangoModelFactory):
    class Meta:
        model = News

    gallery = factory.SubFactory(GalleryFactory)
    url = factory.Faker('url')
    is_active = factory.Faker('pybool')
    scroll_speed = timezone.timedelta(seconds=10)


class CrossBannerFactory(DjangoModelFactory):
    class Meta:
        model = Cross_Banner

    gallery = factory.SubFactory(GalleryFactory)
    type = factory.Iterator(['photo_background', 'photo'])


# ===================
# Email кампании
# ===================
class EmailCampaingFactory(DjangoModelFactory):
    class Meta:
        model = Email_campaing

    status = factory.Iterator(["send", "not sent"])
    template = None


class TamplateEmailFactory(DjangoModelFactory):
    class Meta:
        model = Tamplate_email

    email_campaign = factory.SubFactory(EmailCampaingFactory)
    template_file = factory.django.FileField(filename='template_email.html')