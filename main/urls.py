from django.urls import path
from . import views
app_name = 'main'
urlpatterns = [
    # Для представления на основе класса
    path('', views.index, name='index'),
]