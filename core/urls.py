from django.urls import path
from . import views

urlpatterns = [

    path('cinemas/', views.cinema_list, name='cinema_list'),
    path('cinemas/<slug:cinema_slug>/', views.cinema_detail, name='cinema_detail'),

    path('movies/', views.movie_list, name='movies'),
    path('movies/<slug:movie_slug>/', views.movie_detail, name='movie_detail'),
]