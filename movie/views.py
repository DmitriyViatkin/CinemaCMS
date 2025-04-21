from django.shortcuts import render, get_object_or_404
from .models import Movies
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta


# Create your views here.
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