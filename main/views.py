from django.shortcuts import render, get_object_or_404
from .models import PaigesCinema, Banners, Cross_Banner,PaigesNews, Picture, Promotion,News,Contact
from django.utils.timezone import now
from datetime import timedelta
from movie.models import Movies
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

def contact_paige(request):
    banners = Banners.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='banner_pictures'
        )
    )

    # Fetch contacts with their related data
    contacts_queryset = Contact.objects.select_related('gallery', 'seo_block').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.all(),
            to_attr='all_gallery_images'
        )
    ).all()

    contacts_data = []

    for contact_item in contacts_queryset:  # Проходимо по кожному контакту

        logo_picture = None


        if contact_item.gallery and hasattr(contact_item.gallery, 'all_gallery_images'):
            for pic in contact_item.gallery.all_gallery_images:
                if  pic.image_type == 'logo':
                    logo_picture = pic

        current_latitude = contact_item.latitude if hasattr(contact_item, 'latitude') else None
        current_longitude = contact_item.longitude if hasattr(contact_item, 'longitude') else None

        contacts_data.append({
            'contact': contact_item,
            'logo_picture': logo_picture,

            'latitude': current_latitude,
            'longitude': current_longitude,
        })

    page_seo_data = None
    if contacts_queryset.exists() and contacts_queryset.first().seo_block:
        page_seo_data = contacts_queryset.first().seo_block
    else:
        pass

    context = {
       'contacts_data': contacts_data,
       'banners': banners,
        'page_seo_data': page_seo_data,
        'MAPS_API_KEY': settings.MAPS_API_KEY,
    }
    return render(request, 'main/contact_paige.html', context)

def index(request):
    cross_banner_obj = Cross_Banner.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='gallery'),
            to_attr='cross_banner_pictures'
        )
    ).first()

    cross_banner_background_url = None

    if cross_banner_obj and cross_banner_obj.gallery and cross_banner_obj.gallery.cross_banner_pictures:
        cross_banner_background_url = cross_banner_obj.gallery.cross_banner_pictures[0].image.url

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

        else:
            banner.pictures = []


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



    cinema_page = get_object_or_404(
        PaigesCinema.objects.select_related('gallery', 'seo_block').prefetch_related(
            Prefetch(
                'gallery__pictures',
                queryset=Picture.objects.all(),
                to_attr='all_related_pictures'
            )
        ),
        seo_block__seo_url=slug,
        is_active=True
    )

    main_picture = None
    gallery_pictures_list = []

    # Проверяем, существует ли галерея и есть ли связанные изображения
    if cinema_page.gallery and hasattr(cinema_page.gallery, 'all_related_pictures'):
        for pic in cinema_page.gallery.all_related_pictures:
            if pic.image_type == 'main_picture':
                main_picture = pic
            elif pic.image_type == 'gallery':
                gallery_pictures_list.append(pic) # ИСПРАВЛЕНИЕ: Добавляем картинку в список

    return render(request, 'main/paiges_cinema_detail.html', {
        'seo_block': cinema_page.seo_block,
        'page': cinema_page, # Передаем объект PaigesCinema под более ясным именем
        'main_picture': main_picture,
        'gallery_pictures': gallery_pictures_list
    })

def paiges_news_list(request):
    banners = Banners.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='banner_pictures'
        )
    )
    news = PaigesNews.objects.filter(is_active=True).select_related('gallery').prefetch_related(
        Prefetch('gallery__pictures', queryset=Picture.objects.filter(image_type='main_picture'))
    ).order_by('-date')[:5]

    for item in news:
        item.main_picture = item.gallery.pictures.first() if item.gallery else None
    return render(request, 'main/paiges_news_list.html', {'banners': banners,'news': news})



def paiges_news_detail(request, slug):


    all_gallery_pictures_prefetch = Prefetch(
        'gallery__pictures',
        queryset=Picture.objects.all(),
        to_attr='all_related_pictures'
    )

    paige_news = get_object_or_404(

        PaigesNews.objects.select_related('gallery', 'seo_block').prefetch_related(all_gallery_pictures_prefetch),
        seo_block__seo_url=slug
    )

    main_picture = None
    gallery_pictures_list = []


    if paige_news.gallery and hasattr(paige_news.gallery, 'all_related_pictures'):
        for pic in paige_news.gallery.all_related_pictures:
            if pic.image_type == 'main_picture':
                main_picture = pic
            elif pic.image_type == 'gallery':
                gallery_pictures_list.append(pic)

    return render(request, 'main/paiges_news_detail.html', {
        'seo_block':  paige_news.seo_block,
        'paige_news': paige_news,
        'main_picture': main_picture,
        'gallery_pictures_list': list(gallery_pictures_list),
    })

def promotions_list(request):
    banners = Banners.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='banner_pictures'
        )
    )
    promotions_list = Promotion.objects.select_related('gallery','seo_block').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_picture_list'
        )
    ).order_by('-date')


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
    print(banners)

    return render(request, 'main/action.html', {'banners': banners,'promotions': promotions})



def promotion_detail(request, slug):

    all_gallery_pictures_prefetch = Prefetch(
        'gallery__pictures',
        queryset=Picture.objects.all(),
        to_attr='all_related_pictures'
    )

    promotion = get_object_or_404(
        Promotion.objects.select_related('gallery','seo_block').prefetch_related(all_gallery_pictures_prefetch),
        seo_block__seo_url=slug
    )

    main_picture = None
    gallery_pictures_list = []



    if promotion.gallery and hasattr(promotion.gallery, 'all_related_pictures'):
        for pic in promotion.gallery.all_related_pictures:
            if pic.image_type == 'main_picture':
                main_picture = pic

            elif pic.image_type == 'gallery':
                gallery_pictures_list.append(pic)

    return render(request, 'main/promotion_detail.html', {
        'seo_block': promotion.seo_block,
        'promotion': promotion,
        'main_picture': main_picture,
        'gallery_pictures_list':list( gallery_pictures_list),

    })