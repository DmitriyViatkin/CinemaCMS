from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.utils import timezone
from movie.models import Movies
from users.models import User

from django.forms import formset_factory
from main.models import Gallery, Banners, Cross_Banner, News
from core.models import Cinemas, Halls, Sessions, Seats, Tickets
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import (BlockSEOForm, MovieForm, PictureFormSet, GalleryForm, CinemaForm, HallsForm, SessionsForm,
                    TicketForm, SeatForm, NewsModelFormSet, TopBannerForm, TopBannerModelFormSet, UserForm,
                    SessionFormSet, Picture, CrossBannerForm)
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages

from datetime import timedelta

@staff_member_required
def index(request):
    user_count = User.objects.count()
    ticket_count = Tickets.objects.count()
    movie_count = Movies.objects.count()
    today = timezone.now().date()
    date_from = today - timezone.timedelta(days=30)
    ticket_sales = Tickets.objects.filter(

        session__date__gte=date_from,
        session__date__lte=today
    ).values(

        'session__date'
    ).annotate(

        count=Count('id')
    ).order_by(

        'session__date'
    )
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


    return render(request, 'admin/movies_lists/movies_lists2.html', )

@staff_member_required
def add_movie(request,movie_id=None):
    movie_instance = None
    block_seo_instance = None
    gallery_instance = None
    if movie_id is not None:
        movie_instance = get_object_or_404(Movies, pk=movie_id)
        block_seo_instance = movie_instance.seo_block
        gallery_instance = movie_instance.gallery
        if gallery_instance is None:
            gallery_instance = Gallery.objects.create()
    if request.method == 'POST':

        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        movie_form = MovieForm(request.POST, instance=movie_instance)
        gallery_form = GalleryForm(request.POST,
                                   instance=gallery_instance)
        picture_formset = PictureFormSet(request.POST, request.FILES, instance=gallery_instance)
        if block_seo_form.is_valid() and movie_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid():
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()
            movie_instance = movie_form.save(commit=False)
            movie_instance.seo_block = block_seo_instance
            movie_instance.gallery = gallery_instance
            if movie_id is None and not movie_instance.date:
                movie_instance.date = timezone.now().date()

            movie_instance.save()


            picture_formset.instance = gallery_instance
            picture_formset.save()


            if movie_id is None:

                return redirect('movie_list')
            else:
                return redirect('movie_list')
        else:

            pass
    else:

        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        movie_form = MovieForm(instance=movie_instance)
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet(instance=gallery_instance)


    return render(request, 'admin/movies_lists/add_movies.html', {
        'block_seo_form': block_seo_form,
        'movie_form': movie_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'movie': movie_instance,
    })

@staff_member_required
def delete_movie(request, pk):
    movie = get_object_or_404(Movies, pk=pk)
    movie.delete()
    return redirect('movie_list')

@staff_member_required
def cinema_list(request):
    cinemas_list = Cinemas.objects.all()

    paginator = Paginator(cinemas_list, 10)
    page = request.GET.get('page')
    try:
        cinemas = paginator.page(page)
    except PageNotAnInteger:
        cinemas = paginator.page(1)
    except EmptyPage:
        cinemas = paginator.page(paginator.num_pages)

    context = {'cinemas': cinemas}
    return render(request, 'admin/cinema/cinema_list.html', context)

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

    if request.method == 'POST':

        block_seo_form = BlockSEOForm(request.POST, instance=block_seo_instance)
        cinema_form = CinemaForm(request.POST, instance=cinema_instance)
        gallery_form = GalleryForm(request.POST, instance=gallery_instance)
        picture_formset = PictureFormSet(request.POST, request.FILES, instance=gallery_instance)

        print("POST DATA:", request.POST)
        print("block_seo_form errors:", block_seo_form.errors)
        print("cinema_form errors:", cinema_form.errors)
        print("gallery_form errors:", gallery_form.errors)
        print("picture_formset errors:", picture_formset.errors)

        if block_seo_form.is_valid() and cinema_form.is_valid() and gallery_form.is_valid() and picture_formset.is_valid():
            block_seo_instance = block_seo_form.save()
            gallery_instance = gallery_form.save()

            cinema_instance = cinema_form.save(commit=False)
            cinema_instance.seo_block = block_seo_instance
            cinema_instance.gallery = gallery_instance

            if cinema_id is None and not cinema_instance.date:
                cinema_instance.date = timezone.now().date()

            cinema_instance.save()

            picture_formset.instance = gallery_instance
            picture_formset.save()

            return redirect('cinema_lists')
    else:

        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        cinema_form = CinemaForm(instance=cinema_instance)
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet(instance=gallery_instance)

    return render(request, 'admin/cinema/add_cinema.html', {
        'block_seo_form': block_seo_form,
        'cinema_form': cinema_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'cinema': cinema_instance,
        'form': cinema_form,  # Якщо потрібно для заголовка сторінки
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
def add_halls_create(request, halls_id=None):
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
        picture_formset = PictureFormSet(request.POST, request.FILES, instance=gallery_instance)

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

            picture_formset.instance = gallery_instance
            picture_formset.save()

            return redirect('halls_lists')
    else:
        # Ініціалізуємо форми без даних POST
        block_seo_form = BlockSEOForm(instance=block_seo_instance)
        halls_form = HallsForm(instance=halls_instance)  # Тепер правильна форма
        gallery_form = GalleryForm(instance=gallery_instance)
        picture_formset = PictureFormSet(instance=gallery_instance)

    return render(request, 'admin/halls/add_halls.html', {
        'block_seo_form': block_seo_form,
        'halls_form': halls_form,
        'gallery_form': gallery_form,
        'picture_formset': picture_formset,
        'halls': halls_instance,
        'form': halls_form,  # Якщо потрібно для заголовка сторінки
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
    # Ініціалізуємо формсети для GET-запиту
    # Важливо: queryset=Banners.objects.all() буде брати всі банери.
    # Якщо ти хочеш тільки "топ" банери, переконайся, що твоя модель Banners
    # або її менеджер фільтрує їх правильно, або додай .filter() сюди.
    top_formset = TopBannerModelFormSet(queryset=Banners.objects.all(), prefix='top')
    news_formset = NewsModelFormSet(queryset=News.objects.all(), prefix='news')

    cross_banner_instance = Cross_Banner.objects.select_related('gallery').first()
    cross_banner_form = CrossBannerForm(prefix='cross', instance=cross_banner_instance)

    if request.method == "POST":
        print(f"\n--- Отримано POST запит ---")
        # Перевіряємо, яка кнопка була натиснута
        is_top_form_submitted = 'submit_top_banners_form' in request.POST
        is_news_form_submitted = 'submit_news_banners_form' in request.POST
        is_cross_form_submitted = 'submit_cross_banner_form' in request.POST

        print(f"Кнопка 'Зберегти топ банери' натиснута: {is_top_form_submitted}")
        print(f"Кнопка 'Зберегти новини' натиснута: {is_news_form_submitted}")
        print(f"Кнопка 'Зберегти сквозний банер' натиснута: {is_cross_form_submitted}")

        # === TOP BANNERS ===
        if is_top_form_submitted:
            print(f"Обробка форми Top Banners...")
            # Ініціалізуємо формсет даними POST-запиту
            top_formset = TopBannerModelFormSet(request.POST, request.FILES, prefix='top')

            if top_formset.is_valid():
                print("Top Banners FormSet валідний.")

                # Обробка видалених форм
                if top_formset.deleted_forms:
                    print(f"Кількість форм для видалення (Top): {len(top_formset.deleted_forms)}")
                    for form in top_formset.deleted_forms:
                        if form.instance.pk:
                            try:
                                print(f"  [Видалення] Видалення Top Banner з ID: {form.instance.pk}")
                                if form.instance.gallery:
                                    Picture.objects.filter(gallery=form.instance.gallery).delete()
                                    form.instance.gallery.delete()
                                form.instance.delete()
                                print(f"  [Видалення] Top Banner '{form.instance.pk}' та пов'язані дані видалено успішно.")
                            except Exception as e:
                                print(f"  [Видалення] Помилка при видаленні Top Banner '{form.instance.pk}': {e}")
                                continue
                        else:
                            print(f"  [Видалення] Спроба видалити новий (без PK) Top Banner. Пропускаємо.")
                else:
                    print("Кількість форм для видалення (Top): 0. Немає форм, позначених для видалення.")


                # Обробка нових та змінених форм
                saved_count = 0
                for form_index, form in enumerate(top_formset.forms):
                    # Якщо форма позначена для видалення, пропускаємо її.
                    # Вона вже була оброблена в циклі `deleted_forms` вище.
                    if form.cleaned_data.get('DELETE'):
                        print(f"  [Пропуск] Форма #{form_index} (ID: {form.instance.pk if form.instance.pk else 'новий'}) Top Banner позначена для видалення. Пропускаємо обробку збереження тут.")
                        continue

                    # Пропускаємо абсолютно порожні нові форми, якщо вони не були змінені і не мають зображення.
                    # is_empty_formset_form - допоміжна функція FormSet, щоб визначити, чи це "порожня" форма
                    # (якщо всі її поля Meta.fields порожні).
                    # is_empty_formset_form не є публічним методом, тому краще перевіряти вручну.
                    if form.instance.pk is None and not form.has_changed() and not form.cleaned_data.get('uploaded_image'):
                        print(f"  [Пропуск] Форма #{form_index} Top Banner є новою та порожньою (без змін і без зображення). Пропускаємо.")
                        continue

                    # Зберігаємо екземпляр банера (без зображення)
                    banner_instance = form.save(commit=False) # Це збереже url, text, scroll_speed, is_active

                    if banner_instance.pk is None:
                        # Це нова форма - створюємо нову галерею
                        banner_instance.gallery = Gallery.objects.create()
                        print(f"  [Збереження] Створення нового Top Banner (індекс: {form_index}). Створено нову галерею з ID: {banner_instance.gallery.pk}.")
                    else:
                        # Це існуюча форма
                        print(f"  [Збереження] Оновлення Top Banner з ID: {banner_instance.pk} (індекс: {form_index}).")

                    banner_instance.save() # Зберігаємо екземпляр банера
                    print(f"  [Збереження] Top Banner '{banner_instance.pk}' успішно збережено/оновлено.")
                    saved_count += 1

                    # ОБРОБКА ЗОБРАЖЕННЯ (для 'uploaded_image')
                    uploaded_image_file = form.cleaned_data.get('uploaded_image')
                    # Перевіряємо, чи було завантажено нове зображення
                    if uploaded_image_file:
                        print(f"  [Зображення] Знайдено завантажене зображення для Top Banner '{banner_instance.pk}'.")
                        try:
                            # Шукаємо існуючу Picture або створюємо нову
                            picture, created = Picture.objects.get_or_create(
                                gallery=banner_instance.gallery,
                                image_type='gallery' # Переконайся, що 'gallery' - це коректний image_type
                            )
                            picture.image = uploaded_image_file
                            picture.save()
                            print(f"  [Зображення] Зображення для Top Banner '{banner_instance.pk}' {'створено' if created else 'оновлено'}.")
                        except Exception as e:
                            print(f"  [Зображення] Помилка при збереженні зображення Top Banner '{banner_instance.pk}': {e}")
                    # Перевіряємо, чи користувач очистив існуюче зображення (поле було змінено, але тепер порожнє)
                    elif 'uploaded_image' in form.changed_data and not uploaded_image_file:
                        print(f"  [Зображення] Поле 'uploaded_image' для Top Banner '{banner_instance.pk}' було очищено користувачем.")
                        try:
                            # Видаляємо пов'язане зображення
                            Picture.objects.filter(gallery=banner_instance.gallery, image_type='gallery').delete()
                            print(f"  [Зображення] Зображення для Top Banner '{banner_instance.pk}' видалено (було очищено користувачем).")
                        except Exception as e:
                            print(f"  [Зображення] Помилка при видаленні зображення Top Banner '{banner_instance.pk}' після очищення: {e}")
                    else:
                        print(f"  [Зображення] Зображення для Top Banner '{banner_instance.pk}' не змінилося або не було завантажено.")

                print(f"Top Banners FormSet збережено успішно. Кількість збережених/оновлених: {saved_count}")
                return redirect('banners') # Заміни на правильну назву URL, якщо 'banners' не працює
            else:
                print(f"Помилки валідації форми TOP BANNERS:")
                for i, form in enumerate(top_formset):
                    if form.errors:
                        print(f"  Форма #{i}: {form.errors}")
                        for field, errors in form.errors.items():
                            print(f"    Поле '{field}': {', '.join(errors)}")
                print(f"Дані, що були відправлені для Top Banners (тільки для відладки): {request.POST}, FILES: {request.FILES}")


        # === NEWS BANNERS ===
        elif is_news_form_submitted:
            print(f"Обробка форми News Banners...")
            news_formset = NewsModelFormSet(request.POST, request.FILES, prefix='news')

            if news_formset.is_valid():
                print("News Banners FormSet валідний.")
                if news_formset.deleted_forms:
                    print(f"Кількість форм для видалення (News): {len(news_formset.deleted_forms)}")
                    for form in news_formset.deleted_forms:
                        if form.instance.pk:
                            try:
                                print(f"  [Видалення] Видалення News Banner з ID: {form.instance.pk}")
                                if form.instance.gallery:
                                    Picture.objects.filter(gallery=form.instance.gallery).delete()
                                    form.instance.gallery.delete()
                                form.instance.delete()
                                print(f"  [Видалення] News Banner '{form.instance.pk}' та пов'язані дані видалено успішно.")
                            except Exception as e:
                                print(f"  [Видалення] Помилка при видаленні News Banner '{form.instance.pk}': {e}")
                                continue
                        else:
                            print(f"  [Видалення] Спроба видалити новий (без PK) News Banner. Пропускаємо.")
                else:
                    print("Кількість форм для видалення (News): 0. Немає форм, позначених для видалення.")


                saved_count = 0
                for form_index, form in enumerate(news_formset.forms):
                    if form.cleaned_data.get('DELETE'):
                        print(f"  [Пропуск] Форма #{form_index} (ID: {form.instance.pk if form.instance.pk else 'новий'}) News Banner позначена для видалення. Пропускаємо обробку збереження тут.")
                        continue

                    if form.instance.pk is None and not form.has_changed() and not form.cleaned_data.get('uploaded_image'):
                        print(f"  [Пропуск] Форма #{form_index} News Banner є новою та порожньою (без змін і без зображення). Пропускаємо.")
                        continue

                    news_instance = form.save(commit=False)

                    if news_instance.pk is None:
                        news_instance.gallery = Gallery.objects.create()
                        print(f"  [Збереження] Створення нової News Banner (індекс: {form_index}). Створено нову галерею з ID: {news_instance.gallery.pk}.")
                    else:
                        print(f"  [Збереження] Оновлення News Banner з ID: {news_instance.pk} (індекс: {form_index}).")

                    news_instance.save()
                    print(f"  [Збереження] News Banner '{news_instance.pk}' успішно збережено/оновлено.")
                    saved_count += 1

                    uploaded_image_file = form.cleaned_data.get('uploaded_image')
                    if uploaded_image_file:
                        print(f"  [Зображення] Знайдено завантажене зображення для News Banner '{news_instance.pk}'.")
                        try:
                            picture, created = Picture.objects.get_or_create(
                                gallery=news_instance.gallery,
                                image_type='gallery'
                            )
                            picture.image = uploaded_image_file
                            picture.save()
                            print(f"  [Зображення] Зображення для News Banner '{news_instance.pk}' {'створено' if created else 'оновлено'}.")
                        except Exception as e:
                            print(f"  [Зображення] Помилка при збереженні зображення News Banner '{news_instance.pk}': {e}")
                    elif 'uploaded_image' in form.changed_data and not uploaded_image_file:
                        print(f"  [Зображення] Поле 'uploaded_image' для News Banner '{news_instance.pk}' було очищено.")
                        try:
                            Picture.objects.filter(gallery=news_instance.gallery, image_type='gallery').delete()
                            print(f"  [Зображення] Зображення для News Banner '{news_instance.pk}' видалено (було очищено користувачем).")
                        except Exception as e:
                            print(f"  [Зображення] Помилка при видаленні зображення News Banner '{news_instance.pk}' після очищення: {e}")
                    else:
                        print(f"  [Зображення] Зображення для News Banner '{news_instance.pk}' не змінилося або не було завантажено.")

                print(f"News Banners FormSet збережено успішно. Кількість збережених/оновлених: {saved_count}")
                return redirect('banners')
            else:
                print(f"Помилки валідації форми NEWS BANNERS:")
                for i, form in enumerate(news_formset):
                    if form.errors:
                        print(f"  Форма #{i}: {form.errors}")
                        for field, errors in form.errors.items():
                            print(f"    Поле '{field}': {', '.join(errors)}")
                print(f"Дані, що були відправлені для News Banners (тільки для відладки): {request.POST}, FILES: {request.FILES}")

        # === CROSS BANNER ===
        elif is_cross_form_submitted:
            print(f"Обробка форми Cross Banner...")
            cross_banner_form = CrossBannerForm(request.POST, request.FILES, prefix='cross', instance=cross_banner_instance)

            if cross_banner_form.is_valid():
                cross_banner_obj = cross_banner_form.save(commit=False)

                if cross_banner_obj.pk is None:
                    cross_banner_obj.gallery = Gallery.objects.create()
                    print(f"  [Збереження] Створення нового Cross Banner. Створено нову галерею з ID: {cross_banner_obj.gallery.pk}.")
                else:
                    print(f"  [Збереження] Оновлення Cross Banner з ID: {cross_banner_obj.pk}.")

                cross_banner_obj.save()
                print(f"  [Збереження] Cross Banner '{cross_banner_obj.pk}' збережено.")

                # ОБРОБКА ЗОБРАЖЕННЯ ДЛЯ CROSS BANNER
                # Переконайся, що у CrossBannerForm поле для файлу називається 'uploaded_image'.
                # Якщо ні, заміни на коректну назву (наприклад, 'image').
                uploaded_image_file = cross_banner_form.cleaned_data.get('uploaded_image')
                if uploaded_image_file:
                    print(f"  [Зображення] Знайдено завантажене зображення для Cross Banner '{cross_banner_obj.pk}'.")
                    try:
                        picture, created = Picture.objects.get_or_create(
                            gallery=cross_banner_obj.gallery,
                            image_type='gallery'
                        )
                        picture.image = uploaded_image_file
                        picture.save()
                        print(f"  [Зображення] Зображення для Cross Banner '{cross_banner_obj.pk}' {'створено' if created else 'оновлено'}.")
                    except Exception as e:
                        print(f"  [Зображення] Помилка при збереженні зображення Cross Banner '{cross_banner_obj.pk}': {e}")
                elif 'uploaded_image' in cross_banner_form.changed_data and not uploaded_image_file:
                    print(f"  [Зображення] Поле 'uploaded_image' для Cross Banner '{cross_banner_obj.pk}' було очищено.")
                    try:
                        Picture.objects.filter(gallery=cross_banner_obj.gallery, image_type='gallery').delete()
                        print(f"  [Зображення] Зображення для Cross Banner '{cross_banner_obj.pk}' видалено (було очищено користувачем).")
                    except Exception as e:
                        print(f"  [Зображення] Помилка при видаленні зображення Cross Banner '{cross_banner_obj.pk}' після очищення: {e}")
                else:
                    print(f"  [Зображення] Зображення для Cross Banner '{cross_banner_obj.pk}' не змінилося або не було завантажено.")

                print("Cross Banner збережено успішно.")
                return redirect('banners')
            else:
                print(f"Помилки форми сквозного банера:")
                for field, errors in cross_banner_form.errors.items():
                    print(f"  Поле '{field}': {', '.join(errors)}")
                print(f"Дані, що були відправлені для Cross Banner (тільки для відладки): {request.POST}, FILES: {request.FILES}")

    context = {
        'top_formset': top_formset,
        'news_formset': news_formset,
        'cross_banner_form': cross_banner_form,
    }
    return render(request, 'admin/banner/add_banner.html', context)


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
