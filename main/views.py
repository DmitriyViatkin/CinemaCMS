from django.shortcuts import render, get_object_or_404
from .models import PaigesCinema, Baners

def index(request):
    baners = Baners.objects.all()  # Получаем все баннеры
    # Фильтруем изображения с type='baner'
    for baner in baners:
        baner.pictures = baner.gallery.pictures.filter(image_type='baner')

    # Передаем данные в шаблон
    return render(request, 'main/index1.html', {'baners': baners})



def paiges_cinema_detail(request, slug):
    page = get_object_or_404(PaigesCinema, seo_block__seo_url=slug, is_active=True)
    gallery_pictures = page.gallery.pictures.filter(image_type='gallery') if page.gallery else []
    main_picture = page.gallery.pictures.filter(image_type='main_picture').first() if page.gallery else None

    return render(request, 'main/paiges_cinema_detail.html', {
        'page': page,
        'main_picture': main_picture,
        'gallery_pictures': gallery_pictures
    })
