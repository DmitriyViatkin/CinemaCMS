from ajax_datatable.views import AjaxDatatableView

from movie.models import Movies
from users.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required





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


@staff_member_required
def user_list(request):
    users_list = User.objects.all().order_by('username')

    # search
    search_query = request.GET.get('serch', '')
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query)
        )

    # pagination
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page')

    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    # Date for JSON-response
    data = []
    for user in users_page:
        data.append(
            {
                'id': user.id,
                'Date_of_registration': user.date_joined,
                'date_of_birth': user.date_of_birth,
                'email': user.email,
                'phone_number': user.phone_number,
                'full_name': f"{user.first_name if user.first_name else ''} \
                                {user.last_name if user.last_name else ''}",
                'username': user.username,
                'city': user.city,
            }
        )
        # return json-response
    return JsonResponse({
            'users': data,
            'num_pages': paginator.num_pages,
            'current_page': users_page.number,
            'has_next': users_page.has_next(),
            'has_previous': users_page.has_previous()

        })