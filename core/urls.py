from django.urls import path
from . import views
from .ajax_views import SessionsAjaxView

urlpatterns = [

    path('cinemas/', views.cinema_list, name='cinema_list'),

    path('cinemas/<slug:cinema_slug>/', views.cinema_detail, name='cinema_detail'),

    path('sessions/', views.session_list, name='session_list'),
    path('halls/', views.hall_list, name='halls_list'),
    path('halls/<int:hall_id>/', views.hall_detail, name='hall_detail'),

    path('sessions/<int:session_id>/buy/', views.buy_ticket_view, name='buy_ticket'),

    path('sessions/<int:session_id>/process_purchase/', views.process_ticket_purchase, name='process_ticket_purchase'),



    path('ajax_sessions_data/', SessionsAjaxView.as_view(), name='ajax_sessions_data'),


]