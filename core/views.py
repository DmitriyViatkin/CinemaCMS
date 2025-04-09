from django.shortcuts import render, get_object_or_404
from .models import Cinemas
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def cinema_list(request):
    cinemas_list = Cinemas.objects.all().order_by('title')
    paginator = Paginator(cinemas_list, 10)  # Показывать 10 кинотеатров на странице
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
    context = {'cinema': cinema}
    return render(request, 'core/cinema_detail.html', context)