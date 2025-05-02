from django.urls import path
from . import views
from .views import cinema_list

urlpatterns = [

    path('', views.index, name='admins'),
    path('add_movie/create/', views.add_movie, name='add_movie_create'),
    path('movies_list/list/', views.movie_list, name='movie_list'),
    path('add_movie/<int:movie_id>/', views.add_movie, name='add_movie_edit'),
    path('movies/<int:pk>/delete/', views.delete_movie, name='delete_movie'),


    path('cinema_lists/',views.cinema_list, name='cinema_lists'),
    path('add_cinema/add_cinema_create', views.add_cinema_create, name='add_cinema_create'),
    path('add_cinema/<int:cinema_id>/', views.add_cinema_create ,name='add_cinema_edit'),
    path('cinema_lists/<int:pk>/delete/', views.delete_cinema, name='delete_cinema'),

    path('halls_lists/',views.halls_list, name='halls_lists'),
    path('add_halls/add_halls_create', views.add_halls_create, name='add_halls_create'),
    path('add_halls/<int:halls_id>/', views.add_halls_create ,name='add_halls_edit'),
    path('halls_lists/<int:pk>/delete/', views.delete_halls, name='delete_halls'),

    path('sessions_lists/',views.session_list, name='sessions_list'),
    path('add_sessions/add_sessions', views.add_edit_session, name='add_sessions'),
    path('add_sessions/<int:sessions_id>/', views.add_edit_session,name='add_sessions_edit'),
    path('sessions_lists/<int:pk>/delete/', views.delete_sessions, name='delete_sessions'),
    #path('gallery/edit/<int:gallery_id>/', views.manage_gallery, name='manage_gallery'),

]