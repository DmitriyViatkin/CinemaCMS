from ajax_datatable.views import AjaxDatatableView

from movie.models import Movies



class MovieListDate(AjaxDatatableView):
    model = Movies
    title = 'Фільми'
    initial_order = [["title", "asc"]]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, 'Всі']]
    search_values_separator = '+'


    column_defs = [
         AjaxDatatableView.render_row_tools_column_def(),
         {'name': 'id', 'visible': True},
         {'name': 'title', 'visible': True},
         {'name': ' genre', 'visible': True},
         {'name': 'url_trailer', 'visible': True},
         {'name': ' video_type ', 'visible': True},
         {'name': 'relise_date', 'visible': True},
         {'name': 'age_limit', 'visible': True},
    ]

