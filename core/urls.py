from django.urls import path
from . import views

urlpatterns = [

    path('cinemas/', views.cinema_list, name='cinema_list'),
    path('cinemas/<slug:cinema_slug>/', views.cinema_detail, name='cinema_detail'),

    path('sessions/', views.session_list, name='session_list'),

]