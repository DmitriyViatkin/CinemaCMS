from django.urls import path
from . import views

urlpatterns = [
    # Для представления на основе класса
    path('cinemas/', views.cinema_list, name='cinema_list'),
    path('cinemas/<slug:cinema_slug>/', views.cinema_detail, name='cinema_detail'),
]