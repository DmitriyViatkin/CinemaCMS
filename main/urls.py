from django.urls import path
from . import views
app_name = 'main'
urlpatterns = [
    # Для представления на основе класса
    path('', views.index, name='index'),
    path('page/<slug:slug>/', views.paiges_cinema_detail, name='paiges_cinema_detail'),
]