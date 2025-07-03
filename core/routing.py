from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/seats/<int:session_id>/', consumers.SeatConsumer.as_asgi()),
]