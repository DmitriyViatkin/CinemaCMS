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
    path('add_sessions/<int:session_id>/', views.add_edit_session,name='add_sessions_edit'),
    path('sessions_lists/<int:pk>/delete/', views.delete_sessions, name='delete_sessions'),

    path('seats_list/', views.seats_list, name='seats_list'),
    path('seats_list/add_seats/', views.add_edit_seat, name='add_seats'),
    path('seats_list/<int:session_id>/', views.add_edit_seat, name='edit_seats'),
    path('seats_lists/<int:pk>/delete/', views.delete_seats, name='delete_seats'),

    path('ticket/tickets_lists/', views.tickets_list, name='tickets_lists'),
    path('ticket/tickets_lists/add_ticket/', views.add_edit_ticket, name='add_ticket'),
    path('ticket/tickets_lists/add_ticket/<int:session_id>/', views.add_edit_ticket, name='edit_ticket'),
    path('ticket/tickets_lists/<int:pk>/delete/', views.delete_tickets, name='delete'),

    path('banners/', views.banners_list, name='banners'),
    path('banners/add_banners', views.add_banners, name='add_banners'),
    path('banners/<int:banners_id>/', views.add_banners, name='edit_banners'),
    path('banners/<int:banners_id>/delete_banners/', views.delete_banners, name='delete_banners'),

    path('gallery/', views.gallery_list, name='gallery'),
    path('gallery/add_banners', views.add_gallery, name='add_gallery'),
    path('gallery/<int:gallery_id>/', views.add_gallery, name='edit_gallery'),
    path('gallery/<int:gallery_id>/delete_gallery/', views.delete_gallery, name='delete_gallery'),

    path('user/', views.user_list, name='users'),
    path('user/add_user', views.add_user, name='add_users'),
    path('user/<int:user_id>/edit/', views.add_user, name='edit_users'),
    path('user/<int:user_id>/delete_user/', views.delete_user, name='delete_user')
]