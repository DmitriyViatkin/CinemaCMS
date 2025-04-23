from django.shortcuts import render, get_object_or_404
from .models import PaigesCinema, Baners, Cross_banner,PaigesNews, Picture, Promotion
from django.utils.timezone import now
from datetime import timedelta
from movie.models import Movies
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    # Банери
    baners = Baners.objects.all().select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='baner'))
    )
    for baner in baners:
        if baner.gallery:
            baner.pictures = baner.gallery.pictures.all()
        else:
            baner.pictures = []

    # Фільми, що вже в прокаті (за останні 30 днів)
    movies = Movies.objects.filter(
        relise_date__lte=now()
    ).select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    ).order_by('title')

    for movie in movies:
        movie.main_picture = movie.gallery.pictures.first() if movie.gallery else None

    # ---- Фільми, що скоро вийдуть ----
    coming_soon = Movies.objects.filter(
        relise_date__gt=now(),
        relise_date__lte=now() + timedelta(days=30)
    ).select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    ).order_by('relise_date')

    for movie in coming_soon:
        movie.main_picture = movie.gallery.pictures.first() if movie.gallery else None

    # ---- Новини (тільки активні, останні 5) ----
    news = PaigesNews.objects.filter(is_active=True).select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    ).order_by('-date')[:5]

    for item in news:
        item.main_picture = item.gallery.pictures.first() if item.gallery else None

    return render(request, 'main/index1.html', {
        'baners': baners,
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
    ).order_by('-date_publication')


    for promo in promotions_list:
        if promo.gallery and hasattr(promo.gallery, 'main_picture_list'):
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
