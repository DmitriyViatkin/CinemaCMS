from django.shortcuts import render, get_object_or_404
from .models import PaigesCinema, Banners, Cross_Banner,PaigesNews, Picture, Promotion
from django.utils.timezone import now
from datetime import timedelta
from movie.models import Movies
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    cross_banner_obj = Cross_Banner.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='gallery'),
            to_attr='cross_banner_pictures'
        )
    ).first()

    cross_banner_background_url = None
    # Проверяем наличие cross_banner_obj, затем его gallery,
    # и затем наличие 'cross_banner_pictures' НА ОБЪЕКТЕ GALLERY
    if cross_banner_obj and cross_banner_obj.gallery and cross_banner_obj.gallery.cross_banner_pictures:
        cross_banner_background_url = cross_banner_obj.gallery.cross_banner_pictures[0].image.url
        print(f"URL для фонового кросс-баннера: {cross_banner_background_url}")
    else:
        print("Кросс-баннер не найден, или у него нет галереи/изображений.")
    banners = Banners.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='banner_pictures'
        )
    )




    for banner in banners:
        if banner.gallery:
            banner.pictures = banner.gallery.banner_pictures
            print(f"Для банера {banner.id} знайдено {len(banner.pictures)} зображень.")
        else:
            banner.pictures = []
            print(f"Банер {banner.id} не має галереї.")

    # Фільми, що вже в прокаті
    movies = Movies.objects.filter(
        relise_date__lte=now()
    ).select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_pictures'
        )
    ).order_by('title')

    for movie in movies:
        movie.main_picture = movie.gallery.main_pictures[0] if movie.gallery and movie.gallery.main_pictures else None

    # Фільми, що скоро вийдуть
    coming_soon = Movies.objects.filter(
        relise_date__gt=now(),
        relise_date__lte=now() + timedelta(days=30)
    ).select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_pictures'
        )
    ).order_by('relise_date')

    for movie in coming_soon:
        movie.main_picture = movie.gallery.main_pictures[0] if movie.gallery and movie.gallery.main_pictures else None

    # Новини
    news = PaigesNews.objects.filter(is_active=True).select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_pictures'
        )
    ).order_by('-date')[:5]

    for item in news:
        item.main_picture = item.gallery.main_pictures[0] if item.gallery and item.gallery.main_pictures else None

    return render(request, 'main/index1.html', {
        'cross_banner_background_url': cross_banner_background_url,
        'banners': banners,
        'movies': movies,
        'coming_soon': coming_soon,
        'scroll_interval': 5000,
        'news': news
    })


def paiges_cinema_detail(request, slug):
    print(f"Отримано slug: {slug}")
    try:
        page = get_object_or_404(PaigesCinema, seo_block__seo_url=slug, is_active=True)
        print(f"Знайдено об'єкт PaigesCinema: {page}")
        # ... інший код
    except Exception as e:
        print(f"Помилка при отриманні об'єкта: {e}")
        page = None  # Щоб уникнути помилок у шаблоні, якщо об'єкт не знайдено

    gallery_pictures = []
    main_picture = None

    if page and hasattr(page, 'paiges_cinema_gallery') and page.paiges_cinema_gallery:
        gallery = page.paiges_cinema_gallery
        gallery_pictures = gallery.pictures_in_gallery.filter(image_type='gallery')
        main_picture = gallery.pictures_in_gallery.filter(image_type='main_picture').first()
        print(f"Знайдено зображень галереї: {gallery_pictures.count()}")
        if main_picture:
            print(f"Знайдено головне зображення: {main_picture.image.url}")
        else:
            print("Головне зображення не знайдено.")
    else:
        print("Галерея не знайдена або не існує.")

    return render(request, 'main/paiges_cinema_detail.html', {
        'page': page,
        'main_picture': main_picture,
        'gallery_pictures': gallery_pictures
    })

def paiges_news_list(request):
    news = PaigesNews.objects.filter(is_active=True).select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    ).order_by('-date')[:5]

    for item in news:
        item.main_picture = item.gallery.pictures.first() if item.gallery else None
    return render(request, 'main/paiges_news_list.html', {'news': news})



def paiges_news_detail(request, slug):
    # Отримуємо одну новину за допомогою slug
    news = get_object_or_404(PaigesNews.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_picture_list'
        )
    ).filter(is_active=True), seo_block__seo_url=slug)


    if news.gallery and hasattr(news.gallery, 'main_picture_list'):
        news.main_picture = news.gallery.main_picture_list[0] if news.gallery.main_picture_list else None
    else:
        news.main_picture = None

    return render(request, 'main/paiges_news_detail.html', {
        'news': news,
    })

def promotions_list(request):
    promotions_list = Promotion.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_picture_list'
        )
    ).order_by('-date') # <--- CHANGED FROM 'date_publication' TO 'date'


    for promo in promotions_list:
        if promo.gallery and hasattr(promo.gallery, 'main_picture_list'):
            # Ensure main_picture_list is not empty before accessing index 0
            promo.main_picture = promo.gallery.main_picture_list[0] if promo.gallery.main_picture_list else None
        else:
            promo.main_picture = None

    # Пагінація
    paginator = Paginator(promotions_list, 10)
    page = request.GET.get('page')
    try:
        promotions = paginator.page(page)
    except PageNotAnInteger:
        promotions = paginator.page(1)
    except EmptyPage:
        promotions = paginator.page(paginator.num_pages)


    return render(request, 'main/action.html', {'promotions': promotions})


def promotion_detail(request, slug):
    promotion = get_object_or_404(Promotion.objects.select_related('gallery'), seo_block__seo_url=slug)

    # Перевірка на наявність головного зображення
    main_picture = promotion.gallery.pictures.filter(image_type='main_picture').first() if promotion.gallery else None

    # Отримання всіх зображень галереї
    gallery_pictures = promotion.gallery.pictures.filter(image_type='gallery') if promotion.gallery else []

    return render(request, 'main/promotion_detail.html', {

        'promotion': promotion,
        'main_picture': main_picture,
        'gallery_pictures': gallery_pictures
    })
