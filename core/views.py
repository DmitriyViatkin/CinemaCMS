from django.shortcuts import render, get_object_or_404
from .models import Cinemas, Sessions, Halls, Seats, Tickets
from django.http import HttpResponseRedirect
from main.models import Picture
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Prefetch




def cinema_list(request):
    cinemas_list = Cinemas.objects.select_related('gallery','seo_block').prefetch_related(
        Prefetch(
            'gallery__pictures',
            queryset=Picture.objects.filter(image_type='logo'),
            to_attr='logos'
        )
    ).order_by('title')
    paginator = Paginator(cinemas_list, 10)
    page_number = request.GET.get('page')
    cinemas = paginator.get_page(page_number)

    return render(request, 'core/cinema_list.html', {'cinemas': cinemas})

def cinema_detail(request, cinema_slug):
    cinema = get_object_or_404(Cinemas, seo_block__seo_url=cinema_slug)
    main_picture = cinema.gallery.pictures.filter(image_type="main_picture").first() if hasattr(cinema,
                                                                                                'gallery') and cinema.gallery else None
    halls = cinema.halls.all()
    context = {'cinema': cinema, 'main_picture': main_picture,'halls': halls}
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

    # Получаем все места для текущего зала, сортируем по ряду и номеру места
    hall_seats = Seats.objects.filter(halls=session.hall_id).order_by('number_row', 'seat')

    # Получаем ID забронированных мест для текущего сеанса
    booked_seat_ids = Tickets.objects.filter(session=session).values_list('seat__id', flat=True)

    seat_data_map = {}
    max_row = 0
    max_seat_in_row = {} # Для определения максимального номера места в каждом ряду

    for seat in hall_seats:
        # Обновляем максимальный номер ряда
        if seat.number_row > max_row:
            max_row = seat.number_row

        # Обновляем максимальный номер места в текущем ряду
        if seat.number_row not in max_seat_in_row:
            max_seat_in_row[seat.number_row] = 0
        if seat.seat > max_seat_in_row[seat.number_row]:
            max_seat_in_row[seat.number_row] = seat.seat

        # Определяем текущий статус места
        current_status = seat.status # Исходный статус из БД ('F', 'N')
        if seat.id in booked_seat_ids:
            current_status = "S" # Переопределяем на 'S' (Sold), если место забронировано

        # Сохраняем данные места в map для удобной организации по рядам и местам
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

    # Преобразуем seat_data_map в упорядоченный список рядов и мест,
    # чтобы правильно отобразить "пустые" места (если они есть в схеме, но нет в БД)
    ordered_seat_rows = []
    for r in sorted(seat_data_map.keys()): # Итерируем по отсортированным номерам рядов
        row_seats = []
        # Заполняем места в ряду от 1 до max_seat_in_row для этого ряда
        for s in range(1, max_seat_in_row.get(r, 0) + 1):
            if s in seat_data_map.get(r, {}):
                row_seats.append(seat_data_map[r][s])
            else:
                # Если места нет в БД (например, проход), создаем фиктивное "недоступное" место
                row_seats.append({
                    'id': None, # ID None, так как этого места нет в БД
                    'status': 'N', # Недоступно
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
        # Больше не передаем scheme_hall_json_url
        'seat_rows_current_status_json': json.dumps(ordered_seat_rows), # Это теперь единственный источник данных для схемы
    }

    return render(request, 'core/buy_ticket/buy_ticket.html', context)

 # Убедитесь, что пользователь авторизован
@login_required  # Убедитесь, что пользователь авторизован
def process_ticket_purchase(request, session_id):
     if request.method == 'POST':
         session = get_object_or_404(Sessions, pk=session_id)
         selected_seat_ids_json = request.POST.get('selected_seats')

         if not selected_seat_ids_json:
             # Обработать ошибку: места не выбраны
             # TODO: Добавить систему сообщений для пользователя (например, Django Messages)
             return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))

         selected_seat_ids = json.loads(selected_seat_ids_json)

         if not selected_seat_ids:
             # Обработать ошибку: пустой список мест
             # TODO: Добавить систему сообщений для пользователя
             return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))

         # Создаем список для хранения билетов, которые не удалось создать (если мы хотим об этом сообщать)
         failed_seats_info = []
         purchased_tickets_count = 0

         for seat_id in selected_seat_ids:
             try:
                 seat = get_object_or_404(Seats, pk=seat_id)

                 # Дополнительная проверка на занятость перед созданием билета
                 # Уникальность 'session' и 'seat' в модели Tickets поможет,
                 # но явная проверка тут тоже хороша
                 if Tickets.objects.filter(session=session, seat=seat).exists():
                     # Место уже занято! Не создаем билет для этого места.
                     # Вместо отката транзакции (которой нет), мы просто пропускаем это место
                     # и записываем информацию о неудаче.
                     failed_seats_info.append(f"Ряд {seat.number_row}, Место {seat.seat} уже занято.")
                     continue  # Пропускаем это место и переходим к следующему

                 # Создаем билет
                 ticket = Tickets.objects.create(
                     session=session,
                     movie=session.movie,  # Удобно передать фильм из сеанса
                     seat=seat,
                     profile=request.user,  # Привязываем к текущему пользователю
                     halls=session.hall_id  # Привязываем к залу из сеанса
                 )
                 purchased_tickets_count += 1
                 # purchased_tickets.append(ticket) # Если нужен список созданных объектов Ticket
             except Exception as e:
                 # Обработка других ошибок, которые могут возникнуть при создании билета для конкретного места
                 failed_seats_info.append(f"Ошибка при создании билета для места ID {seat_id}: {e}")
                 print(f"Ошибка при обработке места {seat_id}: {e}")  # Для отладки на сервере

         # После попытки создания билетов для всех выбранных мест
         if purchased_tickets_count > 0:
             # Если хоть какие-то билеты были куплены
             # TODO: Можно передать информацию о failed_seats_info на страницу успеха/отчета
             return HttpResponseRedirect(reverse('profile'))
         else:
             # Если ни одного билета не удалось купить (все были заняты или произошла ошибка)
             # TODO: Добавить систему сообщений для пользователя, чтобы показать failed_seats_info
             print(f"Не удалось купить билеты для выбранных мест: {failed_seats_info}")
             return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))

     return HttpResponseRedirect(reverse('buy_ticket', args=[session_id]))