from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta, datetime, time

# Импортируйте ваши модели
from core.models import Cinemas, Halls, Movies, Sessions  # Убедитесь, что 'core' - это правильное имя вашего приложения


class Command(BaseCommand):
    help = 'Создает сеансы для заданного кинотеатра, фильма, в заданном диапазоне дат и времени.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cinema_id',
            type=int,
            required=True,
            help='ID кинотеатра, для которого создаются сеансы.'
        )
        parser.add_argument(
            '--movie_id',
            type=int,
            required=True,
            help='ID фильма, который будет показан на сеансах.'
        )
        parser.add_argument(
            '--start_date',
            type=str,
            required=True,
            help='Начальная дата в формате YYYY-MM-DD (например, 2025-07-20).'
        )
        parser.add_argument(
            '--end_date',
            type=str,
            required=True,
            help='Конечная дата в формате YYYY-MM-DD (например, 2025-07-25).'
        )
        parser.add_argument(
            '--times',
            type=str,
            required=True,
            help='Список времени сеансов через запятую в формате HH:MM (например, 10:00,13:30,17:00,20:00).'
        )
        parser.add_argument(
            '--price',
            type=int,
            default=55,
            help='Цена билета для сеанса (по умолчанию 55).'
        )
        parser.add_argument(
            '--duration_minutes',
            type=int,
            default=90,  # 1 час 30 минут
            help='Продолжительность сеанса в минутах (по умолчанию 90).'
        )

    def handle(self, *args, **options):
        cinema_id = options['cinema_id']
        movie_id = options['movie_id']
        start_date_str = options['start_date']
        end_date_str = options['end_date']
        times_str = options['times']
        price = options['price']
        duration_minutes = options['duration_minutes']

        try:
            # Получаем объекты кинотеатра, фильма
            cinema = Cinemas.objects.get(pk=cinema_id)  # <-- Определение переменной 'cinema'
            movie = Movies.objects.get(pk=movie_id)  # <-- Определение переменной 'movie'

            # Получаем залы, привязанные к этому кинотеатру
            halls = Halls.objects.filter(cinema=cinema)
            if not halls.exists():
                raise CommandError(
                    f'Для кинотеатра с ID {cinema_id} не найдено ни одного зала. Пожалуйста, создайте залы сначала.')

            # Предположим, что мы будем использовать первый найденный зал для всех сеансов.
            # Если вам нужно более сложное распределение по залам, логику можно доработать.
            hall = halls.first()  # <-- Определение переменной 'hall'

        except Cinemas.DoesNotExist:
            raise CommandError(f'Кинотеатр с ID {cinema_id} не найден.')
        except Movies.DoesNotExist:
            raise CommandError(f'Фильм с ID {movie_id} не найден.')
        except Halls.DoesNotExist:
            raise CommandError(
                f'Зал для кинотеатра с ID {cinema_id} не найден. Убедитесь, что залы привязаны к кинотеатру.')

        # Парсинг дат
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise CommandError('Неверный формат даты. Используйте YYYY-MM-DD.')

        if start_date > end_date:
            raise CommandError('Начальная дата не может быть позже конечной даты.')

        # Парсинг времени сеансов
        session_times = []
        for t_str in times_str.split(','):
            try:
                session_times.append(datetime.strptime(t_str.strip(), '%H:%M').time())
            except ValueError:
                raise CommandError(f'Неверный формат времени: {t_str.strip()}. Используйте HH:MM.')

        # Преобразование продолжительности из минут в time.
        duration_hours = duration_minutes // 60
        duration_remaining_minutes = duration_minutes % 60
        duration_time = time(duration_hours, duration_remaining_minutes)

        # Здесь были исправлены hall.name на hall.title
        self.stdout.write(
            f'Начинаем создание сеансов для кинотеатра: {cinema.title}, фильм: {movie.title} в зале: {hall.title}')
        self.stdout.write(f'Диапазон дат: с {start_date} по {end_date}')
        self.stdout.write(f'Время сеансов: {", ".join([t.strftime("%H:%M") for t in session_times])}')
        self.stdout.write(f'Цена: {price}, Продолжительность: {duration_minutes} минут')

        current_date = start_date
        sessions_created_count = 0

        while current_date <= end_date:
            for session_time in session_times:
                if not Sessions.objects.filter(
                        cinema=cinema,
                        hall_id=hall,
                        movie=movie,
                        date=current_date,
                        time_session=session_time
                ).exists():
                    session = Sessions.objects.create(
                        cinema=cinema,
                        hall_id=hall,
                        movie=movie,
                        price=price,
                        time_session=session_time,
                        duration=duration_time,
                        date=current_date
                    )
                    sessions_created_count += 1
                    # Здесь были исправлены session.hall_id.name на session.hall_id.title
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Успешно создан сеанс: {session.movie.title} '
                            f'в {session.cinema.title} ({session.hall_id.title}) '
                            f'на {session.date} в {session.time_session.strftime("%H:%M")}'
                        )
                    )
                else:
                    # Здесь были исправлены hall.name на hall.title
                    self.stdout.write(
                        self.style.WARNING(
                            f'Сеанс уже существует: {movie.title} '  # Исправлено movies.title на movie.title
                            f'в {cinema.title} ({hall.title}) '  # Исправлено cinemas.title на cinema.title
                            f'на {current_date} в {session_time.strftime("%H:%M")}. Пропускаем.'
                        )
                    )
            current_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Создано {sessions_created_count} новых сеансов.'))
"""
 python manage.py add_sesions   --cinema_id 9   --movie_id 5   --start_date 2025-07-16   --end_date 2025-09-25   --times 14:00,16:00


"""