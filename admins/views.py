from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from movie.models import Movies
from users.models import User

from django.db.models import Prefetch


from main.models import Gallery, Banners, Cross_Banner, News
from core.models import Cinemas, Halls, Sessions, Seats, Tickets
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import (BlockSEOForm, MovieForm, PictureFormSet, GalleryForm, CinemaForm, HallsForm, SessionsForm,
                    TicketForm,SeatForm, PictureFormSet1,  BannersFormSet,  NewsFormSet,  PictureForm, UserForm, SessionFormSet , Picture,  CrossBannerForm , modelformset_factory)
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string


@staff_member_required
def index(request):
    user_count = User.objects.count()
    ticket_count = Tickets.objects.count()
    movie_count = Movies.objects.count()
    today = timezone.now().date()
    date_from = today - timezone.timedelta(days=30)
    ticket_sales = (Tickets.objects.filter(session__date__gte=date_from,session__date__lte=today).
                    values('session__date').annotate(count=Count('id')).order_by('session__date' ))
    chart_labels = [item['session__date'].strftime('%Y-%m-%d') for item in ticket_sales]
    chart_data = [item['count'] for item in ticket_sales]
    knob_data = {
        'category1': 5,
        'category2': 10,
        'category3': 20,
    }

    context = {
        'user_count': user_count,
        'ticket_count': ticket_count,
        'movie_count' : movie_count,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'knob_data': knob_data,
    }

    return render(request,'admin/index.html', context)

@staff_member_required
def movie_list(request):
    movies_list = Movies.objects.all().select_related('gallery').order_by('title')
    paginator = Paginator(movies_list, 10)  # Показывать 10 фильмов на странице

    page = request.GET.get('page')
    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        # Если page не целое число, показать первую страницу
        movies = paginator.page(1)
    except EmptyPage:
        # Если page вне диапазона (например, 9999), показать последнюю страницу
        movies = paginator.page(paginator.num_pages)
    for movie in movies:
        if movie.gallery:
            movie.main_picture = movie.gallery.pictures.filter(image_type="main_picture").first()
        else:
            movie.main_picture = None

    context = {'movies': movies}
    return render(request, 'admin/movies_lists/movies_lists.html', context)






@staff_member_required
def add_movie(request, movie_id=None):

    movie_instance = None
    block_seo_instance = None
    gallery_instance = None
    main_picture_form = None

    if movie_id is not None:
        movie_instance = get_object_or_404(Movies, pk=movie_id)
        block_seo_instance = movie_instance.seo_block
        gallery_instance = movie_instance.gallery
        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()

    if request.method=='POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        movie_form = MovieForm(request.POST, instance=movie_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)
        picture_formset = PictureFormSet1( request.POST, request.FILES, instance=gallery_instance, prefix='pictures' )
        main_picture_form = PictureForm(request.POST, request.FILES, prefix='main_picture_form', initial={
                                                        'image_type': 'main_picture', 'gallery': gallery_instance})

        if block_seo_form.is_valid() and movie_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid() and main_picture_form.is_valid():
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()
            movie_instance = movie_form.save(commit=False)
            movie_instance.seo_block = block_seo_instance
            movie_instance.gallery = gallery_instance

            movie_instance.save()

            # Сохранение главной картинки через отдельную форму
            if main_picture_form.cleaned_data.get('image'):
                main_picture = main_picture_form.save(commit=False)
                main_picture.gallery = gallery_instance
                main_picture.image_type = 'main_picture'
                main_picture.save()
                movie_instance.main_picture = main_picture.image
                movie_instance.save()

            for picture_form in picture_formset:
                if picture_form.cleaned_data and not picture_form.cleaned_data.get('DELETE', False) and picture_form.cleaned_data.get('image'):
                    picture = picture_form.save(commit=False)
                    picture.gallery = gallery_instance
                    picture.save()
                elif picture_form.cleaned_data.get('DELETE', False) and picture_form.instance.pk:
                    picture_form.instance.delete()

            return redirect('movie_list')
        else:
            print("Form validation failed")
            print("block_seo_form.errors:", block_seo_form.errors)
            print("movie_form.errors:", movie_form.errors)
            print("gallery_form.errors:", gallery_form.errors)
            print("picture_formset.errors:", picture_formset.errors)
            print("main_picture_form.errors:", main_picture_form.errors)
            return render(request, 'admin/movies_lists/add_movies.html', {
                'block_seo_form': block_seo_form,
                'movie_form': movie_form,
                'gallery_form': gallery_form,
                'picture_formset': picture_formset,
                'main_picture_form': main_picture_form,
                'movie': movie_instance,
            })

    else:
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        movie_form = MovieForm(instance=movie_instance)
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet1(
            instance=gallery_instance,
            prefix='pictures'
        )
        main_picture_form = PictureForm(prefix='main_picture_form', initial={'image_type': 'main_picture',
                                                                             'gallery': gallery_instance})

    return render(request, 'admin/movies_lists/add_movies.html', {
        'block_seo_form': block_seo_form,
        'movie_form': movie_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'main_picture_form': main_picture_form,
        'movie': movie_instance,
    })




@staff_member_required
def delete_movie(request, pk):
    movie = get_object_or_404(Movies, pk=pk)
    movie.delete()
    return redirect('movie_list')

@staff_member_required
def cinema_list(request):
    cinemas_list = Cinemas.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='logo'),
            to_attr='logos'
        )
    ).order_by('title')
    paginator = Paginator(cinemas_list, 10)
    page_number = request.GET.get('page')
    cinemas = paginator.get_page(page_number)
    return render(request, 'admin/cinema/cinema_list.html', {'cinemas': cinemas})

@staff_member_required
def add_cinema_create(request, cinema_id=None):
    cinema_instance = None
    block_seo_instance = None
    gallery_instance = None



    if cinema_id is not None:
        cinema_instance = get_object_or_404(Cinemas, pk=cinema_id)
        block_seo_instance = cinema_instance.seo_block
        gallery_instance = cinema_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
    else:
        gallery_instance = Gallery.objects.create()

    if request.method == 'POST':
        cinema_form = CinemaForm(request.POST, instance=cinema_instance)
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)

        picture_formset = PictureFormSet1(request.POST, request.FILES,
                                         queryset=Picture.objects.filter(gallery=gallery_instance),
                                         prefix='pictures')

        logo_form = PictureForm(request.POST, request.FILES, prefix='logo')
        banner_form = PictureForm(request.POST, request.FILES, prefix='banner')

        if (cinema_form.is_valid() and block_seo_form.is_valid() and gallery_form.is_valid()
                and picture_formset.is_valid() and logo_form.is_valid() and banner_form.is_valid()):

            # Save related objects
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()

            # Save cinema
            cinema_instance = cinema_form.save(commit=False)
            cinema_instance.seo_block = block_seo_instance
            cinema_instance.gallery = gallery_instance
            if cinema_id is None and not cinema_instance.date:
                cinema_instance.date = timezone.now().date()
            cinema_instance.save()

            # Save logo
            logo_instance = logo_form.save(commit=False)
            logo_instance.gallery = gallery_instance
            logo_instance.image_type = 'logo'
            logo_instance.save()

            # Save banner
            banner_instance = banner_form.save(commit=False)
            banner_instance.gallery = gallery_instance
            banner_instance.image_type = 'main_picture'
            banner_instance.save()

            # Save gallery pictures
            pictures = picture_formset.save(commit=False)
            for picture in pictures:
                picture.gallery = gallery_instance
                picture.image_type = 'gallery'
                picture.save()
            picture_formset.save_m2m()

            return redirect('cinema_lists')

        else:
            print("Form Errors:")
            print("cinema_form:", cinema_form.errors)
            print("seo_form:", block_seo_form.errors)
            print("gallery_form:", gallery_form.errors)
            print("picture_formset:", picture_formset.errors)
            print("logo_form:", logo_form.errors)
            print("banner_form:", banner_form.errors)

    else:
        cinema_form = CinemaForm(instance=cinema_instance)
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        gallery_form = GalleryForm(instance=gallery_instance)

        picture_formset = PictureFormSet1(
            queryset=Picture.objects.filter(gallery=gallery_instance),
            prefix='pictures'
        )

        # ok to prefill preview
        logo_instance = Picture.objects.filter(gallery=gallery_instance, image_type='logo').first()
        banner_instance = Picture.objects.filter(gallery=gallery_instance, image_type='main_picture').first()
        logo_form = PictureForm(instance=logo_instance, prefix='logo')
        banner_form = PictureForm(instance=banner_instance, prefix='banner')

    halls = Halls.objects.filter(cinema=cinema_instance) if cinema_instance else Halls.objects.none()

    return render(request, 'admin/cinema/add_cinema.html', {
        'block_seo_form': block_seo_form,
        'cinema_form': cinema_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'cinema': cinema_instance,
        'form': cinema_form,
        'logo_form': logo_form,
        'banner_form': banner_form,
        'halls': halls,
    })

@staff_member_required
def delete_cinema(request, pk):
    cinema = get_object_or_404(Cinemas, pk=pk)
    cinema.delete()
    return redirect('cinema_list')

@staff_member_required
def halls_list(request):

        halls_list = Halls.objects.all()

        paginator = Paginator(halls_list, 10)
        page = request.GET.get('page')
        try:
            halls = paginator.page(page)
        except PageNotAnInteger:
            halls = paginator.page(1)
        except EmptyPage:
            halls = paginator.page(paginator.num_pages)

        context = {'halls': halls}
        return render(request, 'admin/halls/halls_lists.html', context)

@staff_member_required
def add_halls_create(request,   halls_id=None):
    halls_instance = None
    block_seo_instance = None
    gallery_instance = None

    if halls_id is not None:
        halls_instance = get_object_or_404(Halls, pk=halls_id)
        block_seo_instance = halls_instance.seo_block
        gallery_instance = halls_instance.gallery

        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()

    if request.method == 'POST':
        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        halls_form = HallsForm(request.POST, instance=halls_instance)  # Тут використовуємо HallsForm
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)
        picture_formset = PictureFormSet1(request.POST, request.FILES, instance=gallery_instance, prefix='pictures')
        logo_form = PictureForm(request.POST, request.FILES, prefix='logo')
        banner_form = PictureForm(request.POST, request.FILES, prefix='banner')

        print("POST DATA:", request.POST)
        print("block_seo_form errors:", block_seo_form.errors)
        print("halls_form errors:", halls_form.errors)
        print("gallery_form errors:", gallery_form.errors)
        print("picture_formset errors:", picture_formset.errors)

        if block_seo_form.is_valid() and halls_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid():
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()

            halls_instance = halls_form.save(commit=False)
            halls_instance.seo_block = block_seo_instance
            halls_instance.gallery = gallery_instance

            if halls_id is None and not halls_instance.date:
                halls_instance.date = timezone.now().date()

            halls_instance.save()

            logo_instance = logo_form.save(commit=False)
            logo_instance.gallery = gallery_instance
            logo_instance.image_type = 'logo'
            logo_instance.save()

            # Save banner
            banner_instance = banner_form.save(commit=False)
            banner_instance.gallery = gallery_instance
            banner_instance.image_type = 'main_picture'
            banner_instance.save()

            picture_formset.instance = gallery_instance
            picture_formset.save()

            return redirect( 'cinema_lists')
    else:
        # Ініціалізуємо форми без даних POST
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        halls_form = HallsForm(instance=halls_instance)  # Тепер правильна форма
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet1(instance=gallery_instance)
        logo_instance = Picture.objects.filter(gallery=gallery_instance, image_type='logo').first()
        banner_instance = Picture.objects.filter(gallery=gallery_instance, image_type='main_picture').first()
        logo_form = PictureForm(instance=logo_instance, prefix='logo')
        banner_form = PictureForm(instance=banner_instance, prefix='banner')

    return render(request, 'admin/halls/add_halls.html', {
        'block_seo_form': block_seo_form,
        'halls_form': halls_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'halls': halls_instance,
        'form': halls_form,
        'logo_form':logo_form,
        'banner_form': banner_form
    })

@staff_member_required
def delete_halls(request, pk):
    halls = get_object_or_404(Halls, pk=pk)
    halls.delete()
    return redirect('halls_list')

@staff_member_required
def session_list(request):
    session_list = Sessions.objects.all()

    paginator = Paginator(session_list, 10)
    page = request.GET.get('page')
    try:
        sessions = paginator.page(page)
    except PageNotAnInteger:
        sessions = paginator.page(1)
    except EmptyPage:
        sessions = paginator.page(paginator.num_pages)

    context = {'sessions': sessions}
    return render(request, 'admin/session/sessions_list.html', context)

@staff_member_required
def add_edit_session(request, session_id=None):
    if request.method == 'POST':
        formset = SessionFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('sessions_list')
    else:
        # Важливо: передаємо пустий queryset, щоб уникнути заповнених форм
        formset = SessionFormSet(queryset=Sessions.objects.none())

    return render(request, 'admin/session/add_sessions.html', {
        'session_formset': formset,
        'session': None
    })

@staff_member_required
def delete_sessions(request, pk):
        sessions = get_object_or_404(Sessions, pk=pk)

        sessions.delete()

        return redirect('sessions_list')

@staff_member_required




def seats_list(request: HttpRequest) -> HttpResponse:
    seats_list = Seats.objects.select_related('halls').order_by('number_row', 'seat')
    paginator = Paginator(seats_list, 10)
    page_number = request.GET.get('page')

    try:
        seats = paginator.page(page_number)
    except PageNotAnInteger:
        seats = paginator.page(1)
    except EmptyPage:
        seats = paginator.page(paginator.num_pages)

    context = {'seats': seats}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('admin/seats_list/seats_table_partial.html', context, request=request)
        return HttpResponse(html)
    else:
        return render(request, 'admin/seats_list/seats_list.html', context)

@staff_member_required
def add_edit_seat(request):
    seat_id = request.GET.get('seat_id') or request.POST.get('seat_id')
    if seat_id:
        seat_instance = get_object_or_404(Seats, id=seat_id)
        form = SeatForm(request.POST or None, instance=seat_instance)
    else:
        form = SeatForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('seats_list')

    seats = Seats.objects.all().order_by('number_row', 'seat')
    return render(request, 'admin/seats_list/add_seats.html', {
        'form': form,
        'seats': seats,
    })

@staff_member_required
def delete_seats(request, pk):
        seat = get_object_or_404(Seats, pk=pk)

        seat.delete()

        return redirect('seats_list')

@staff_member_required
def tickets_list(request):

    tickets_list = Tickets.objects.all()


    paginator = Paginator(tickets_list, 10)
    page = request.GET.get('page')
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)

    context = {
        'tickets': tickets,
    }
    return render(request, 'admin/tickets/tickets_list.html', context)

@staff_member_required
def add_edit_ticket(request, session_id=None):
    session_instance = None
    ticket_instance = None

    if session_id:
        session_instance = get_object_or_404(Sessions, id=session_id)
        try:
            ticket_instance = Tickets.objects.get(session=session_instance)
        except Tickets.DoesNotExist:
            ticket_instance = Tickets(session=session_instance)

    if request.method == 'POST':
        form = TicketForm(request.POST, instance=ticket_instance)
        if form.is_valid():
            saved_ticket = form.save()

            seat_to_update = saved_ticket.seat
            if seat_to_update:
                seat_to_update.status = 'S'
                seat_to_update.save()

            return redirect('tickets_lists')
    else:
        form = TicketForm(instance=ticket_instance)

    context = {
        'form': form,
        'session': session_instance,
    }
    return render(request, 'admin/tickets/add_tickets.html', context)

@staff_member_required
def delete_tickets (request, pk):
        tickets = get_object_or_404(Tickets, pk=pk)
        if request.method == 'POST':
            tickets.delete()
            return redirect('tickets_lists')
        tickets.delete()
        return redirect('tickets_lists')


@staff_member_required
def add_banners(request):
    banner_formset = BannersFormSet(request.POST or None, request.FILES or None, queryset=Banners.objects.all(), prefix='top_banners')
    cross_banner_instance = Cross_Banner.objects.first()
    cross_banner_form = CrossBannerForm(request.POST or None, request.FILES or None, instance=cross_banner_instance, prefix='cross_banner')
    news_formset = NewsFormSet(request.POST or None, request.FILES or None, queryset=News.objects.all(), prefix='news')


    if request.method=='POST':

        if "which_form_is_it" in request.POST:
            which_form_is_submiting = request.POST["which_form_is_it"]

            if str(which_form_is_submiting) == "this_is_form_banner":

                if banner_formset.is_valid():

                    banner_formset.save()

                    for form in banner_formset.forms:
                        if not form.cleaned_data:
                            continue
                        banner = form.instance

                        # Перевіряємо, чи передано новий файл
                        main_picture_file = form.cleaned_data.get('main_picture')

                        # Якщо новина не має галереї — створюємо її
                        if banner and not banner.gallery:
                            banner.gallery = Gallery.objects.create()
                            banner.save()

                        # Якщо є галерея — отримуємо або створюємо Picture з типом main_picture
                        if banner.gallery:
                            picture = banner.gallery.pictures.filter(image_type='main_picture').first()
                            if not picture:
                                picture = Picture(gallery=banner.gallery, image_type='main_picture')

                            # Оновлюємо зображення, тільки якщо новий файл передано
                            if main_picture_file:
                                picture.image = main_picture_file

                            picture.save()

                    banner_formset.save()

                    return redirect('add_banners')
                else:
                    pass


            elif str(which_form_is_submiting) == "this_is_form_cross_banner":

                if cross_banner_form.is_valid():
                    cross_banner = cross_banner_form.save()
                    image_file = request.FILES.get('cross_banner-image')

                    if cross_banner:
                        if not cross_banner.gallery_id:
                            cross_banner.gallery = Gallery.objects.create()
                            cross_banner.save()

                        if cross_banner.gallery:
                            picture = cross_banner.gallery.pictures.first()

                            if not picture:
                                picture = Picture(gallery=cross_banner.gallery)

                            if image_file:
                                picture.image = image_file
                                picture.save()
                            else:
                                pass
                    return redirect('add_banners')

                else:
                    pass
            elif str(which_form_is_submiting)=="this_is_form_news":

                if news_formset.is_valid():

                    news_formset.save()
                    for form in news_formset.forms:
                        if not form.cleaned_data:
                            continue
                        news = form.instance

                        # Перевіряємо, чи передано новий файл
                        main_picture_file = form.cleaned_data.get('main_picture')

                        # Якщо новина не має галереї — створюємо її
                        if news and not news.gallery:
                            news.gallery = Gallery.objects.create()
                            news.save()

                        # Якщо є галерея — отримуємо або створюємо Picture з типом main_picture
                        if news.gallery:
                            picture = news.gallery.pictures.filter(image_type='main_picture').first()
                            if not picture:
                                picture = Picture(gallery=news.gallery, image_type='main_picture')

                            # Оновлюємо зображення, тільки якщо новий файл передано
                            if main_picture_file:
                                picture.image = main_picture_file

                            picture.save()

                    return redirect('add_banners')
                else:
                    pass
        else:
                pass

    form_data = []
    for form in banner_formset.forms:
        image_url = None
        if form.instance.gallery:
            picture = form.instance.gallery.pictures.filter(image_type='main_picture').first()
            if picture and picture.image:
                image_url = picture.image.url
        form_data.append({'form': form, 'image_url': image_url})

    news_form_data = []
    for form in news_formset.forms:
        image_url = None
        if form.instance.gallery:
            picture = form.instance.gallery.pictures.filter(image_type='main_picture').first()
            if picture and picture.image:
                image_url = picture.image.url
        news_form_data.append({'form': form, 'image_url': image_url})

    return render(request, 'admin/banner/add_banner.html', {
        'formset': banner_formset,
        'form_data': form_data,
        'cross_banner_form': cross_banner_form,
        'news_formset': news_formset,
        'news_form_data': news_form_data,
    })

@staff_member_required
def banners_list(request):
    banners_list = Banners.objects.select_related('gallery').all().order_by('id')

    paginator = Paginator(banners_list, 10)
    page = request.GET.get('page')
    try:
        banners = paginator.page(page)
    except PageNotAnInteger:
        banners = paginator.page(1)
    except EmptyPage:
        banners = paginator.page(paginator.num_pages)

    context = {'banners': banners}

    return render(request, 'admin/banner/banner.html', context)

@staff_member_required
def delete_banners(request, banners_id):
     banner = get_object_or_404(Banners, pk=banners_id)
     if request.method == 'POST':
         banner.delete()

     return redirect('banners')



@staff_member_required
def user_list(request):

    user_list_all = User.objects.all()
    paginator = Paginator(user_list_all, 10)
    page_number = request.GET.get('page')

    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    context = {'users': users_page}
    return render(request, 'admin/user/user_lists.html', context)

@staff_member_required
def add_user(request, user_id=None):
    user_instance = None
    is_edit = False

    if user_id:

        user_instance = get_object_or_404(User, pk=user_id)
        is_edit = True


    if request.method == 'POST':

        form = UserForm(request.POST, instance=user_instance)


        if form.is_valid():

            form.save()

            return redirect('users')

    else:
        form = UserForm(instance=user_instance)
    return render(request, 'admin/user/add_user.html', {
        'form': form,
        'user_instance': user_instance,
        'is_edit': is_edit,
    })

@staff_member_required
def delete_user(request, users_id):
    user = get_object_or_404(User, pk=users_id)

    if request.method == 'POST': # <<< Видалення відбувається тільки тут
        user.delete()
        return redirect('users')
    else: #
        return redirect('users')