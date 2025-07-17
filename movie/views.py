from django.shortcuts import render, get_object_or_404
from .models import Movies
from main.models import Picture
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import date, timedelta, datetime
from django.utils.timezone import now
from core.models import Sessions, Cinemas
from django.db.models import Q
from collections import defaultdict

# Create your views here.
def movie_list(request):
    movies_list = Movies.objects.all().select_related('gallery',  ).order_by('title')

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
                  Prefetch('gallery__pictures')
              ),
        id=movie_id
    )

    today = date.today()

    sessions = Sessions.objects.filter(movie=movie, date__gte=today).order_by('date', 'time_session')
    # Тільки сеанси з датою >= сьогоднішня

    selected_city = request.GET.get('city')
    if selected_city:
        sessions = sessions.filter(cinema__city=selected_city)

    selected_date_str = request.GET.get('date')
    selected_date = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            sessions = sessions.filter(date=selected_date)
        except ValueError:
            pass

    is_2d = request.GET.get('is_2d') == '1'
    is_3d = request.GET.get('is_3d') == '1'
    is_imax = request.GET.get('is_imax') == '1'

    movie_filter = Q()
    if is_2d:
        movie_filter &= Q(movie__is_2d=True)
    if is_3d:
        movie_filter &= Q(movie__is_3d=True)
    if is_imax:
        movie_filter &= Q(movie__is_imax=True)

    if movie_filter:
        sessions = sessions.filter(movie_filter)


    available_dates = (
        Sessions.objects.filter(movie=movie, date__gte=today)
        .values_list('date', flat=True)
        .distinct()
        .order_by('date')
    )

    all_cities = Cinemas.objects.values_list('city', flat=True).distinct().order_by('city')
    sessions_by_cinema = defaultdict(list)

    for session in sessions:
        sessions_by_cinema[session.cinema.id].append(session)

    main_picture = movie.gallery.pictures.filter(image_type="main_picture").first() if movie.gallery else None

    context = {
        'movie': movie,
        'seo_block': movie.seo_block,
        'main_picture': main_picture,
        'gallery_pictures': movie.gallery.pictures.all() if movie.gallery else [],
        'sessions': sessions,
        'all_cities': all_cities,
        'selected_city': selected_city,
        'selected_date': selected_date,
        'available_dates': available_dates,
        'filter': {
            'is_2d': is_2d,
            'is_3d': is_3d,
            'is_imax': is_imax,
        },
        'sessions_by_cinema': dict(sessions_by_cinema),
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