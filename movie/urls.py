from django.urls import path
from . import views

urlpatterns = [

    path('movies/', views.movie_list, name='movies_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    #path('sessions/', views.session_list, name='session_list'),
    path('movie/', views.movie_soon, name='movies_soon')
]