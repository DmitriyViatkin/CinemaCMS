from django.shortcuts import render, get_object_or_404
from .models import Cinemas, Sessions, Halls, Seats, Tickets
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json

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
    for cinema in cinemas:
        if hasattr(cinema, 'gallery') and cinema.gallery:
            # Фільтруємо зображення, щоб знайти логотип
            logos = [pic for pic in cinema.gallery.pictures.all() if pic.image_type == 'logo']
            # Якщо знайдено логотип, додаємо його до об'єкта кінотеатру
            cinema.logo = logos[0] if logos else None
        else:
            cinema.logo = None

    context = {'cinemas': cinemas }
    return render(request, 'core/cinema_list.html', context)


def cinema_detail(request, cinema_slug):
    cinema = get_object_or_404(Cinemas, seo_block__seo_url=cinema_slug)

    main_picture = None
    logo_picture = None
    gallery_pictures = []

    if hasattr(cinema, 'gallery') and cinema.gallery:
        main_picture = cinema.gallery.pictures.filter(image_type="main_picture").first()
        logo_picture = cinema.gallery.pictures.filter(image_type="logo").first()  # This gets a Picture object
        gallery_pictures = cinema.gallery.pictures.filter(image_type="gallery").all()

    halls = cinema.halls.all()

    context = {
        'cinema': cinema,
        'main_picture': main_picture,
        'halls': halls,
        'logo': logo_picture,  # Pass the Picture object
        'gallery_pictures': gallery_pictures,
    }
    return render(request, 'core/cinema_detail.html', context)

def session_list(request):
    sessions = Sessions.objects.select_related('hall_id', 'movie')
    context = {
        'sessions': sessions
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

def hall_detail(request, hall_id):

    hall = get_object_or_404(Halls, pk=hall_id)

    context = {'hall': hall}
    return render(request, 'hall/hall_detail.html', context)


def buy_ticket_view(request, session_id):
    session = get_object_or_404(
        Sessions.objects.select_related('cinema', 'hall_id', 'movie'),
        pk=session_id
    )


    hall_seats = Seats.objects.filter(halls=session.hall_id).order_by('number_row', 'seat')


    booked_seat_ids = Tickets.objects.filter(session=session).values_list('seat__id', flat=True)

    seat_data_map = {}
    max_row = 0
    max_seat_in_row = {}

    for seat in hall_seats:

        if seat.number_row > max_row:
            max_row = seat.number_row


        if seat.number_row not in max_seat_in_row:
            max_seat_in_row[seat.number_row] = 0
        if seat.seat > max_seat_in_row[seat.number_row]:
            max_seat_in_row[seat.number_row] = seat.seat


        current_status = seat.status
        if seat.id in booked_seat_ids:
            current_status = "S"


        if seat.number_row not in seat_data_map:
            seat_data_map[seat.number_row] = {}

        seat_data_map[seat.number_row][seat.seat] = {
            'id': seat.id,
            'status': current_status,
            'is_vip': seat.is_vip,
            'price': float(seat.price),
            'row_number': seat.number_row,
            'seat_number': seat.seat
        }


    ordered_seat_rows = []
    for r in sorted(seat_data_map.keys()):
        row_seats = []

        for s in range(1, max_seat_in_row.get(r, 0) + 1):
            if s in seat_data_map.get(r, {}):
                row_seats.append(seat_data_map[r][s])
            else:

                row_seats.append({
                    'id': None, #
                    'status': 'N',
                    'is_vip': False,
                    'price': 0.0,
                    'row_number': r,
                    'seat_number': s
                })
        ordered_seat_rows.append({'row_number': r, 'seats': row_seats})

    context = {
        'session': session,
        'cinema_title': session.cinema.title,
        'hall_title': session.hall_id.title,
        'session_time': session.time_session,
        'session_date': session.date,
        'movie_title': session.movie.title,

        'seat_rows_current_status_json': json.dumps(ordered_seat_rows),
    }

    return render(request, 'core/buy_ticket/buy_ticket.html', context)


@login_required
def process_ticket_purchase(request, session_id):
     if request.method == 'POST':
         session = get_object_or_404(Sessions, pk=session_id)
         selected_seat_ids_json = request.POST.get('selected_seats')

         if not selected_seat_ids_json:

             return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))

         selected_seat_ids = json.loads(selected_seat_ids_json)

         if not selected_seat_ids:

             return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))


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

             except Exception as e:

                 failed_seats_info.append(f"Ошибка при создании билета для места ID {seat_id}: {e}")
                 print(f"Ошибка при обработке места {seat_id}: {e}")


         if purchased_tickets_count > 0:

             return HttpResponseRedirect(reverse('profile'))
         else:

             print(f"Не удалось купить билеты для выбранных мест: {failed_seats_info}")
             return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))

     return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))