from django.contrib.admin.templatetags.admin_list import pagination
from django.shortcuts import render, get_object_or_404
from .models import Cinemas, Movies
from main.models import Block_SEO
from main.models import Gallery, Picture
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def cinema_list(request):
    cinemas_list = Cinemas.objects.all().order_by('title')
    paginator = Paginator(cinemas_list, 10)
    page = request.GET.get('page')
    try:
        cinemas = paginator.page(page)
    except PageNotAnInteger:
        cinemas = paginator.page(1)
    except EmptyPage:
        cinemas = paginator.page(paginator.num_pages)

    context = {'cinemas': cinemas}
    return render(request, 'core/cinema_list.html', context)
# Create your views here.
def cinema_detail(request, cinema_slug):
    cinema = get_object_or_404(Cinemas, seo_block__seo_url=cinema_slug)
    halls = cinema.halls.all()  # Получаем все залы, связанные с этим кинотеатром
    context = {'cinema': cinema, 'halls': halls}
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
    context = {'movies':movies}
    return render(request, 'core/movies_list.html',context)



def movie_detail(request, movie_slug):
    movies = get_object_or_404(Movies, seo_block__seo_url=movie_slug)


    main_picture = movies.gallery.picture.filter(image_type="main_picture").first() if movies.gallery else None
    gallery_pictures = movies.gallery.picture.filter(image_type="gallery") if movies.gallery else []

    context = {
        'movies': movies,
        'main_picture': main_picture,
        'gallery_pictures': gallery_pictures,
    }
    return render(request, 'core/movie_detail.html', context)