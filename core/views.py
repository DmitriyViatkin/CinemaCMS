from debug_toolbar.management.commands.debugsqlshell import PrintQueryWrapper
from django.shortcuts import render, get_object_or_404
from .models import Cinemas, Sessions, Halls

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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

def cinema_detail(request, cinema_slug):
    cinema = get_object_or_404(Cinemas, seo_block__seo_url=cinema_slug)
    main_picture = cinema.gallery.pictures.filter(image_type="main_picture").first() if hasattr(cinema,
                                                                                                'gallery') and cinema.gallery else None
    halls = cinema.halls.all()  # Получаем все залы, связанные с этим кинотеатром
    context = {'cinema': cinema, 'main_picture': main_picture,'halls': halls}
    return render(request, 'core/cinema_detail.html', context)

def session_list(request):
    sessions = Sessions.objects.select_related('hall_id', 'movie')
    context = {
        'sessions': sessions
    }
    return render(request, 'core/session_list.html', context)

def hall_list(request):
    hall_list = Halls.objects.all()

    paginator = Paginator(hall_list, 10)
    page = request.GET.get('page')
    try:
        hall_list = paginator.page(page)
    except PageNotAnInteger:
        hall_list = paginator.page(1)
    except EmptyPage:
        hall_list = paginator.page(paginator.num_pages)

    context = {'hall_list': hall_list}
    return render(request, 'hall/hall_list.html', context)

def hall_detail(request, hall_id):

    hall = get_object_or_404(Halls, pk=hall_id)

    context = {'hall': hall}
    return render(request, 'hall/hall_detail.html', context)
