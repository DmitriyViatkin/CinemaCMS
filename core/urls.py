from django.urls import path
from . import views

urlpatterns = [

    path('cinemas/', views.cinema_list, name='cinema_list'),

    path('cinemas/<slug:cinema_slug>/', views.cinema_detail, name='cinema_detail'),

    path('sessions/', views.session_list, name='session_list'),
    path('halls/', views.hall_list, name='halls_list'),
    path('halls/<int:hall_id>/', views.hall_detail, name='hall_detail'),

]