from django.shortcuts import render, get_object_or_404
from .models import Movies
from main.models import Picture
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta
from django.utils.timezone import now


# Create your views here.
def movie_list(request):
    movies_list = Movies.objects.all().select_related('gallery').order_by('title')

    paginator = Paginator(movies_list, 10)
    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    for movie in movies:
        if movie.gallery:
            movie.main_picture = movie.gallery.pictures.filter(image_type="main_picture").first()
        else:
            movie.main_picture = None

    context = {'movies': movies}
    return render(request, 'movie/movies_list.html', context)



def movie_detail(request, movie_id):
    movie = get_object_or_404(
        Movies.objects.select_related('seo_block', 'gallery')
              .prefetch_related(
                  Prefetch('gallery__pictures'),
                  'movie_sessions' # Make sure 'movie_sessions' is the correct related_name for Sessions
              ),
        # --- ИЗМЕНЕНИЕ ЗДЕСЬ: фильтруем по 'id' вместо 'seo_block__seo_url' ---
        id=movie_id
    )

    main_picture = movie.gallery.pictures.filter(image_type="main_picture").first() if movie.gallery else None

    context = {
        'movie': movie,
        'main_picture': main_picture,
        'gallery_pictures': movie.gallery.pictures.all() if movie.gallery else [],
        'sessions': movie.movie_sessions.all()
    }
    return render(request, 'movie/movie_detail.html', context)

def movie_soon(request):
    next_30_days = now() + timedelta(days=30)

    coming_soon = Movies.objects.filter(
        relise_date__gt=now(),
        relise_date__lte=next_30_days
    ).select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_picture_list'
        )
    ).order_by('relise_date')

    # Додаємо main_picture до кожного фільму
    for movie in coming_soon:
        if movie.gallery and hasattr(movie.gallery, 'main_picture_list'):
            movie.main_picture = movie.gallery.main_picture_list[0] if movie.gallery.main_picture_list else None
        else:
            movie.main_picture = None

    paginator = Paginator(coming_soon, 10)
    page = request.GET.get('page')

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    context = {'movies': movies}
    return render(request, 'movie/movies_list.html', context)