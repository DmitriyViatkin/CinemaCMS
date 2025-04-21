from django.contrib.admin.templatetags.admin_list import pagination
from django.shortcuts import render, get_object_or_404
from .models import Cinemas, Sessions
from main.models import Block_SEO
from main.models import Gallery, Picture
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta


def cinema_list(request):
    cinemas_list = Cinemas.objects.select_related('gallery').prefetch_related('gallery__pictures').order_by('title')

    paginator = Paginator(cinemas_list, 10)
    page = request.GET.get('page')
    try:
        cinemas = paginator.page(page)
    except PageNotAnInteger:
        cinemas = paginator.page(1)
    except EmptyPage:
        cinemas = paginator.page(paginator.num_pages)

    context = {'cinemas': cinemas }
    return render(request, 'core/cinema_list.html', context)
# Create your views here.
def cinema_detail(request, cinema_slug):
    cinema = get_object_or_404(Cinemas, seo_block__seo_url=cinema_slug)
    main_picture = cinema.gallery.pictures.filter(image_type="main_picture").first() if hasattr(cinema,
                                                                                                'gallery') and cinema.gallery else None
    halls = cinema.halls.all()  # Получаем все залы, связанные с этим кинотеатром
    context = {'cinema': cinema, 'main_picture': main_picture,'halls': halls}
    return render(request, 'core/cinema_detail.html', context)

def movie_list(request):
    movies_list = Movies.objects.all().order_by('title')
    paginator = Paginator(movies_list, 10)
    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies  = paginator.page(paginator.num_pages)

    for movie in movies:
        if movie.gallery:
            movie.main_picture = movie.gallery.pictures.filter(image_type="main_picture").first()
        else:
            movie.main_picture = None

    context = {'movies': movies}
    return render(request, 'core/movies_list.html', context)



def movie_detail(request, movie_slug):
    movies = get_object_or_404(Movies, seo_block__seo_url=movie_slug)

    main_picture = movies.gallery.pictures.filter(image_type="main_picture").first() if hasattr(movies,
                                                                                                'gallery') and movies.gallery else None
    #gallery_pictures = movies.gallery.pictures.filter(image_type="gallery") if hasattr(movies,
       #                                                                                'gallery') and movies.gallery else []


    context = {
        'movies': movies,
        'main_picture': main_picture,
        #'gallery_pictures': gallery_pictures,
    }
    return render(request, 'core/movie_detail.html', context)

def session_list(request):
    sessions = Sessions.objects.select_related('hall_id', 'movie_id').order_by('date', 'time_session')
    context = {
        'sessions': sessions
    }
    return render(request, 'core/session_list.html', context)


def movie_soon(request):
    today = date.today()
    next_week = today + timedelta(days=7)

    # Отримуємо фільми з релізом протягом тижня
    movies_list = Movies.objects.filter(relise_date__lte=next_week).order_by('relise_date')

    paginator = Paginator(movies_list, 10)
    page = request.GET.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    # Додаємо головне зображення
    for movie in movies:
        movie.main_picture = (
            movie.gallery.pictures.filter(image_type="main_picture").first()
            if movie.gallery else None
        )

    context = {'movies': movies}
    return render(request, 'core/movies_list.html', context)