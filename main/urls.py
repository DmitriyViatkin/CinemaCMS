from django.urls import path
from . import views
app_name = 'main'
urlpatterns = [
    # Для представления на основе класса
    path('', views.index, name='home'),
    path('page/<slug:slug>/', views.paiges_cinema_detail, name='paiges_cinema_detail'),

    path('news/', views.paiges_news_list, name='paiges_news_list'),
    path('news/<slug:slug>/', views.paiges_news_detail, name='paiges_news_detail'),

    path('promotion/', views.promotions_list, name='promotions_list'),
    path('promotion/<slug:slug>/', views.promotion_detail, name='promotion_detail'),

]