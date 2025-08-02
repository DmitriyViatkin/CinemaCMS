from dateutil.utils import today
from django.shortcuts import render, get_object_or_404
from .models import Cinemas, Sessions, Halls, Seats, Tickets
from django.http import HttpResponseRedirect
from main.models import Picture
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Prefetch
from collections import defaultdict
from movie.models import Movies
from main.models import Banners,Contact
import locale
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import date, datetime
from django.utils import timezone
from datetime import date
from django.utils.formats import date_format




import locale
try:
    locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
except locale.Error:
    pass


def cinema_list(request):
    banners = Banners.objects.select_related('gallery').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='banner_pictures'
        )
    )

    cinemas_list = Cinemas.objects.select_related('gallery','seo_block').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='main_picture'),
            to_attr='main_picture'
        )
    ).order_by('title')
    paginator = Paginator(cinemas_list, 10)
    page_number = request.GET.get('page')
    cinemas = paginator.get_page(page_number)

    return render(request, 'core/cinema_list.html', {'banners': banners,'cinemas': cinemas})

def cinema_detail(request, cinema_slug):
    all_gallery_pictures_prefetch = Prefetch(
        'gallery__pictures',
        queryset=Picture.objects.all(),
        to_attr='all_gallery_images'
    )

    halls_prefetch = Prefetch(
        'halls',
        queryset=Halls.objects.all().order_by('title'),
        to_attr='prefetched_halls'
    )
    cinema = get_object_or_404(
        Cinemas.objects.select_related('seo_block', 'gallery')
                       .prefetch_related(all_gallery_pictures_prefetch, halls_prefetch),
        seo_block__seo_url=cinema_slug
    )

    main_picture = None
    logo_picture = None
    gallery_pictures_list = []

    if cinema.gallery and hasattr(cinema.gallery, 'all_gallery_images'):
        for pic in cinema.gallery.all_gallery_images:
            if pic.image_type == 'main_picture':
                main_picture = pic

            elif pic.image_type == 'logo':
                logo_picture = pic

            elif pic.image_type == 'gallery':
                gallery_pictures_list.append(pic)



    today = timezone.localdate()

    today_sessions = Sessions.objects.filter(cinema=cinema,date=today).select_related('movie').order_by('time_session')

    halls = cinema.prefetched_halls

    context = {
        'seo_block': cinema.seo_block,
        'cinema': cinema,
        'main_picture': main_picture,
        'logo_picture': logo_picture,
        'halls': halls ,
        'today_sessions': today_sessions ,
        'gallery_pictures_list': list(gallery_pictures_list )
    }
    return render(request, 'core/cinema_detail.html', context)
#
def hall_detail(request, hall_id):
    today = date.today()

    all_gallery_pictures_prefetch = Prefetch(
        'gallery__pictures',
        queryset=Picture.objects.all(),
        to_attr='all_gallery_images'
    )

    hall = get_object_or_404(
        Halls.objects.select_related('seo_block', 'gallery')
                     .prefetch_related(all_gallery_pictures_prefetch),
        pk=hall_id
    )

    main_picture = None
    gallery_pictures_list = []
    # logo_picture was declared but never initialized if image_type == 'logo' not found
    # and was not in context. Keeping it out as it looks like debug/incomplete code.
    logo_picture = None

    if hall.gallery and hasattr(hall.gallery, 'all_gallery_images'):
        for pic in hall.gallery.all_gallery_images:
            if pic.image_type == 'main_picture':
                main_picture = pic
            elif pic.image_type == 'logo':
                logo_picture = pic
            elif pic.image_type == 'gallery':
                gallery_pictures_list.append(pic)

    hall_sessions = Sessions.objects.filter(hall_id=hall.id, date__gte=today).select_related('movie').order_by('date', 'time_session')

    context = {
        'seo_block': hall.seo_block,
        'hall': hall,
        'main_picture': main_picture,
        'hall_sessions': hall_sessions,
        'gallery_pictures_list': gallery_pictures_list,
        'logo_picture': logo_picture, # Included for consistency if it's always desired
    }

    return render(request, 'hall/hall_detail.html', context)



def session_list(request, cinema=None, hall=None):
    date_filter = request.GET.get('date')
    cinema_filter = request.GET.get('cinema')
    hall_filter = request.GET.get('hall')
    movie_id_filter = request.GET.get('movie')

    is_2d = request.GET.get('is_2d') == '1'
    is_3d = request.GET.get('is_3d') == '1'
    is_imax = request.GET.get('is_imax') == '1'

    sessions = Sessions.objects.select_related('hall_id__cinema', 'movie').filter(date__gte=date.today())

    if date_filter:
        sessions = sessions.filter(date=date_filter)
    if cinema_filter:
        sessions = sessions.filter(hall_id__cinema__id=cinema_filter)
    if hall_filter:
        sessions = sessions.filter(hall_id__id=hall_filter)
    if movie_id_filter:
        sessions = sessions.filter(movie__id=movie_id_filter)

    format_filter = Q()
    if is_2d:
        format_filter &= Q(movie__is_2d=True)
    if is_3d:
        format_filter &= Q(movie__is_3d=True)
    if is_imax:
        format_filter &= Q(movie__is_imax=True)

    if format_filter:
        sessions = sessions.filter(format_filter)

    grouped_sessions = defaultdict(list)
    for session in sessions.order_by('date'):
        day_name = date_format(session.date, 'l', use_l10n=True)
        date_str = session.date.strftime('%d.%m.%Y')
        grouped_sessions[(day_name.capitalize(), date_str)].append(session)

    all_cinemas = Cinemas.objects.all()

    if cinema_filter:
        try:
            halls_for_dropdown = Halls.objects.filter(cinema__id=cinema_filter).order_by('title')
        except ValueError:
            halls_for_dropdown = Halls.objects.none()
    else:
        halls_for_dropdown = Halls.objects.none()

    context = {
        'grouped_sessions': dict(grouped_sessions),
        'cinemas': Cinemas.objects.all(),
        'movies': Movies.objects.all(),
        'selected_date': date_filter,
        'selected_cinema': cinema_filter,
        'selected_movie': movie_id_filter,
        'selected_hall': hall_filter,
        'halls': halls_for_dropdown,
        'filter': {
            'is_2d': is_2d,
            'is_3d': is_3d,
            'is_imax': is_imax,
        },
    }
    return render(request, 'core/session_2.html', context)
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

@login_required

def buy_ticket_view(request, session_id):
    """
    Відображає сторінку покупки квитків для конкретного сеансу.
    Надає схему залу з актуальними статусами місць.
    """
    session = get_object_or_404(
        Sessions.objects.select_related('cinema', 'hall_id', 'movie')
        .prefetch_related(
            Prefetch('hall_id__gallery__pictures',
                     queryset=Picture.objects.order_by('id')),
            Prefetch('movie__gallery__pictures',
                     queryset=Picture.objects.order_by('id'))
        ),
        pk=session_id
    )

    hall = session.hall_id
    movie = session.movie

    # Отримуємо головне зображення залу або перше доступне
    hall_picture = None
    if hall.gallery:
        hall_picture = hall.gallery.pictures.filter(image_type="main_picture").first() or \
                       hall.gallery.pictures.first()

    # Отримуємо головне зображення фільму або перше доступне
    movie_picture = None
    if movie.gallery:
        movie_picture = movie.gallery.pictures.filter(image_type="main_picture").first() or \
                        movie.gallery.pictures.first()

    # Отримуємо всі місця для конкретного залу, відсортовані за рядом та номером місця
    hall_seats = Seats.objects.filter(halls=hall).order_by('number_row', 'seat')

    # Отримуємо ID всіх місць, які вже зайняті (продані або заброньовані) на цей сеанс
    # Оскільки модель Tickets не має поля 'status', ми просто знаємо, що місце зайняте.
    occupied_seat_ids = Tickets.objects.filter(session=session).values_list('seat__id', flat=True)
    occupied_seat_ids = list(occupied_seat_ids)  # Перетворюємо на список для швидкого пошуку

    # Отримуємо ID місць, які належать поточному авторизованому користувачеві
    user_tickets_seat_ids = []
    if request.user.is_authenticated:
        user_tickets_seat_ids = Tickets.objects.filter(
            session=session,
            profile=request.user
        ).values_list('seat__id', flat=True)
        user_tickets_seat_ids = list(user_tickets_seat_ids)

    # Структура для зберігання даних про місця, організованих за рядами
    seat_data_map = {}
    max_row = 0
    max_seat_in_row = {}  # Для відстеження максимального номера місця в кожному ряду

    # Обробка кожного місця в залі
    for seat in hall_seats:
        max_row = max(max_row, seat.number_row)
        max_seat_in_row[seat.number_row] = max(max_seat_in_row.get(seat.number_row, 0), seat.seat)

        current_display_status = seat.status  # Беремо базовий статус місця з моделі Seats

        is_user_ticket_for_session = (seat.id in user_tickets_seat_ids)
        is_occupied_by_any_ticket = (seat.id in occupied_seat_ids)

        # Логіка визначення статусу місця для відображення на схемі:
        if is_user_ticket_for_session:
            # Якщо місце належить поточному користувачеві, воно завжди позначається як 'U' (квиток користувача)
            current_display_status = "U"
        elif is_occupied_by_any_ticket:
            # Якщо місце зайняте будь-яким квитком (але не поточним користувачем)
            # Тут обмеження: оскільки Tickets не має status, ми не знаємо, чи це 'S' чи 'b'.
            # Якщо базовий status у Seats був 'F' (вільний), але місце зайняте,
            # ми примусово встановлюємо його як 'S' (продано/зайнято).
            if current_display_status == 'F':
                current_display_status = 'S'  # За замовчуванням вважаємо "проданим/зайнятим"
            # Якщо current_display_status вже 'S', 'b' або 'N' (і місце зайняте), залишаємо його як є.
        # В іншому випадку (місце не зайняте), current_display_status залишається таким, як у Seats.status (тобто 'F' або 'N').

        # Додаємо дані про місце до структури
        seat_data_map.setdefault(seat.number_row, {})[seat.seat] = {
            'id': seat.id,
            'status': current_display_status,  # 'U', 'S', 'b', 'F', або 'N'
            'is_vip': seat.is_vip,
            'price': float(seat.price or session.price),  # Використовуємо ціну місця, або ціну сеансу
            'row_number': seat.number_row,
            'seat_number': seat.seat,
        }

    # Перетворюємо карту місць на впорядкований список рядів для фронтенду
    ordered_seat_rows = []
    for row in sorted(seat_data_map.keys()):
        row_seats = []
        # Заповнюємо місця в ряду, враховуючи пропущені номери місць (як "недоступні")
        for seat_num in range(1, max_seat_in_row[row] + 1):
            row_seats.append(seat_data_map[row].get(seat_num, {
                'id': None,
                'status': 'N',
                'is_vip': False,
                'price': 0.0,
                'row_number': row,
                'seat_number': seat_num,
            }))
        ordered_seat_rows.append({'row_number': row, 'seats': row_seats})

    # Підготовка контексту для шаблону
    context = {
        'session': session,
        'cinema_title': session.cinema.title,
        'hall_title': hall.title,
        # Corrected: Use session.time_session for time and session.date for date
        'session_time': session.time_session.strftime('%H:%M') if session.time_session else None,  # Format time
        'session_date': session.date.strftime('%Y-%m-%d') if session.date else None,  # Format date
        'movie_title': movie.title,
        'session_price': float(session.price),
        'hall_picture': hall_picture.image.url if hall_picture and hall_picture.image else None,
        'movie_picture': movie_picture.image.url if movie_picture and movie_picture.image else None,
        # JSON-дані про статус місць для JavaScript
        'seat_rows_current_status_json': json.dumps(ordered_seat_rows),
        # JSON-дані про місця поточного користувача для JavaScript (для класу 'user-ticket')
        'user_tickets_seat_ids': json.dumps(user_tickets_seat_ids),
    }

    return render(request, 'core/buy_ticket/buy_ticket.html', context)

@login_required
def process_ticket_purchase(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(Sessions, pk=session_id)
        selected_seat_ids_json = request.POST.get('selected_seats')

        redirect_url = request.META.get('HTTP_REFERER')
        if not redirect_url:
            redirect_url = reverse('buy_ticket', args=[session_id])

        if not selected_seat_ids_json:
            return HttpResponseRedirect(redirect_url)

        selected_seat_ids = json.loads(selected_seat_ids_json)

        if not selected_seat_ids:
            return HttpResponseRedirect(redirect_url)

        failed_seats_info = []
        purchased_tickets_count = 0

        for seat_id in selected_seat_ids:
            try:
                seat = get_object_or_404(Seats, pk=seat_id)

                if Tickets.objects.filter(session=session, seat=seat).exists():
                    failed_seats_info.append(f"Ряд {seat.number_row}, Место {seat.seat} уже занято.")
                    continue

                ticket = Tickets.objects.create(
                    session=session,
                    movie=session.movie,
                    seat=seat,
                    profile=request.user,
                    halls=session.hall_id
                )
                purchased_tickets_count += 1
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"session_{session_id}",
                    {
                        'type': 'update_seats'
                    }
                )
            except Exception as e:
                failed_seats_info.append(f"Ошибка при создании билета для места ID {seat_id}: {e}")

        if purchased_tickets_count > 0:
            if failed_seats_info:
                pass
            return HttpResponseRedirect(redirect_url)
        else:
            return HttpResponseRedirect(redirect_url)

    return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))

@login_required
def process_ticket_books(request, session_id):
    if request.method == 'POST':
        session = get_object_or_404(Sessions, pk=session_id)
        selected_seat_ids_json = request.POST.get('selected_seats')

        redirect_url = request.META.get('HTTP_REFERER') or reverse('buy_ticket', args=[session_id])

        if not selected_seat_ids_json:
            return HttpResponseRedirect(redirect_url)

        selected_seat_ids = json.loads(selected_seat_ids_json)

        if not selected_seat_ids:
            return HttpResponseRedirect(redirect_url)

        failed_seats_info = []
        purchased_tickets_count = 0

        for seat_id in selected_seat_ids:
            try:
                seat = get_object_or_404(Seats, pk=seat_id)

                # Перевірка, чи місце вже зайняте
                if Tickets.objects.filter(session=session, seat=seat).exists() or seat.status == 'S':
                    failed_seats_info.append(f"Ряд {seat.number_row}, Місце {seat.seat} вже зайнято.")
                    continue

                # Створення квитка
                Tickets.objects.create(
                    session=session,
                    movie=session.movie,
                    seat=seat,
                    profile=request.user,
                    halls=session.hall_id
                )

                # Оновлення статусу місця
                seat.status = 'b'
                seat.save(update_fields=['status'])

                purchased_tickets_count += 1

                # WebSocket оновлення
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"session_{session_id}",
                    {
                        'type': 'update_seats'
                    }
                )
            except Exception as e:
                failed_seats_info.append(f"Помилка при створенні квитка для місця ID {seat_id}: {e}")

        return HttpResponseRedirect(redirect_url)

    return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))