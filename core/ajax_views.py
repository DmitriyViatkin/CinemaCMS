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

        AjaxDatatableView.render_row_tools_column_def(),


        {"name": "id", "visible": False, "searchable": False},


        {"name": "cinema", "foreign_field": "cinema__title", "visible": True, "title": "Кінотеатр"},
        {"name": "hall", "foreign_field": "hall_id__title", "visible": True, "title": "Зал"},
        {"name": "movie", "foreign_field": "movie__title", "visible": True, "title": "Фільм", },


        {"name": "time_session", "visible": True, "searchable": False, "title": "Час сеансу"},
        {"name": "duration", "visible": True, "searchable": False, "title": "Тривалість"},
        {"name": "date", "visible": True, "title": "Дата"},
        {
            'name': 'go_to_movie',
            'title': 'Фильм',
            'placeholder': True,
            'searchable': False,
            'orderable': False,
        },
        {
            'name': 'buy_ticket',
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
                          {obj.movie.title}
                       </a>
                   """
        else:
            row['go_to_movie'] = '-'


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


def get_unique_cinemas(request):
    cinemas = list(
        Sessions.objects.values_list('cinema__title', flat=True).distinct().order_by('cinema__title')
    )
    print(cinemas)
    return JsonResponse({"values": cinemas})

def get_unique_movie(request):
    # Исправлено: имя поля внешнего ключа в модели Sessions - 'movie' (без 's')
    # Исправлено: два подчеркивания для lookup `__`
    movies = list(
        Sessions.objects.values_list('movie__title', flat=True).distinct().order_by('movie__title')
    )
    return JsonResponse({"values": movies})

def get_unique_hall(request):
    # Исправлено: имя поля внешнего ключа в модели Sessions - 'hall_id'
    halls = list(
        Sessions.objects.values_list('hall_id__title', flat=True).distinct().order_by('hall_id__title')
    )
    return JsonResponse({"values": halls})