from ajax_datatable.views import AjaxDatatableView
from django.urls import reverse
from django.http import JsonResponse
from .models import Sessions



class SessionsAjaxView(AjaxDatatableView):
    model = Sessions
    title = "Сеанси"
    initial_order = [["cinema__title", "asc"]]  # Початкове сортування
    length_menu = [[10, 25, 50, -1], [10, 25, 50, "Всі"]]  # Додайте "Всі"

    column_defs = [
        # Стовпець для дій (редагування/видалення)
        AjaxDatatableView.render_row_tools_column_def(),

        # ID (можливо, не потрібно показувати, але корисно для відладки)
        {"name": "id", "visible": False, "searchable": False},  # Зазвичай ID не показують

        # Для пов'язаних полів: 'name' - це назва стовпця для AjaxDatatable,
        # 'foreign_field' - це шлях до поля в моделі
        {"name": "cinema", "foreign_field": "cinema__title", "visible": True, "title": "Кінотеатр"},
        {"name": "hall", "foreign_field": "hall_id__title", "visible": True, "title": "Зал"},
        {"name": "movie", "foreign_field": "movie__title", "visible": True, "title": "Фільм", },

        # Для власних полів моделі Sessions
        {"name": "time_session", "visible": True, "searchable": False, "title": "Час сеансу"},
        {"name": "duration", "visible": True, "searchable": False, "title": "Тривалість"},
        {"name": "date", "visible": True, "title": "Дата"},
    ]

    def render_columns(self, row, column):
        # 'row' - це об'єкт моделі Sessions для поточного рядка
        # 'column' - це словник з визначенням стовпця (один з елементів column_defs)

        if column.get('name') == 'movie':
            movie_instance = row.movie  # Отримуємо об'єкт Movie
            if movie_instance:
                # ЗВЕРНІТЬ УВАГУ: Переконайтеся, що ваш Movie-модель має поле 'slug'
                # Якщо ні, і ви хочете використовувати PK, змініть ваш urls.py для фільмів на <int:pk>
                # і тоді тут використовуйте 'pk': movie_instance.pk
                try:
                    url = reverse('movie_detail', kwargs={'movie_slug': movie_instance.slug})
                    return f'<a href="{url}">{movie_instance.title}</a>'
                except Exception as e:
                    # Якщо виникає помилка при reverse (наприклад, slug не існує), обробіть її
                    print(f"Error reversing URL for movie '{movie_instance.title}': {e}")
                    return movie_instance.title  # Повертаємо просто назву, якщо посилання не вдалося створити
            return '—'  # Якщо фільму немає

        # Для інших стовпців просто повертаємо стандартний рендеринг
        # Базова реалізація handle_row_data повертає значення поля за замовчуванням
        return super().render_columns(row, column)

    def get(self, request, *args, **kwargs):
        # 🔒 Захист від прямого GET без параметрів DataTables
        if 'draw' not in request.GET:
            return JsonResponse({"error": "Invalid request. Must be a DataTables AJAX call."}, status=400)
        return super().get(request, *args, **kwargs)


