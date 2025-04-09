from django.urls import path
from . import views

urlpatterns = [
    # Для представления на основе класса
    path('/', views.index, name='main'),
]