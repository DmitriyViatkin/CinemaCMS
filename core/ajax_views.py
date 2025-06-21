from ajax_datatable.views import AjaxDatatableView
from django.urls import reverse
from django.http import JsonResponse
from .models import Sessions



class SessionsAjaxView(AjaxDatatableView):
    model = Sessions
    title = "Сеанси"
    initial_order = [["cinema__title", "asc"]]  # Початкове сортування
    length_menu = [[10, 25, 50, -1], [10, 25, 50, "Всі"]]  # Додайте "Всі"
    render_html = True

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
        {
            'name': 'go_to_movie',  # Первая колонка: "Фильм"
            'title': 'Фильм',
            'placeholder': True,
            'searchable': False,
            'orderable': False,
        },
        {
            'name': 'buy_ticket',  # Вторая колонка: "Купить билет"
            'title': 'Купить билет',
            'placeholder': True,
            'searchable': False,
            'orderable': False,
        },
    ]

    def customize_row(self, row, obj):
        # Кнопка "Фильм"
        if obj.movie:
            movie_url = reverse('movie_detail', kwargs={'movie_id': obj.movie.id})
            row['go_to_movie'] = f"""
                       <a href="{movie_url}" class="btn btn-info btn-sm">
                          Фильм
                       </a>
                   """
        else:
            row['go_to_movie'] = '-'

        # Кнопка "Купить билет"
        if obj.id:
            buy_ticket_url = reverse('buy_ticket', kwargs={'session_id': obj.id})
            row['buy_ticket'] = f"""
                       <a href="{buy_ticket_url}" class="btn btn-success btn-sm">
                           Купить билет
                       </a>
                   """
        else:
            row['buy_ticket'] = '-'

        return row


def get(self, request, *args, **kwargs):
        if 'draw' not in request.GET:
            return JsonResponse({"error": "Invalid request. Must be a DataTables AJAX call."}, status=400)
        return super().get(request, *args, **kwargs)


