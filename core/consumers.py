import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from core.models import Tickets
class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):


        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"session_{self.session_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


        await self.send_seat_status()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'refresh':
            await self.send_seat_status()


    async def send_seat_status(self):
        # вызов ORM синхронный, обернём в sync_to_async
        taken_seats = await sync_to_async(list)(
            Tickets.objects.filter(session_id=self.session_id).values_list('seat_id', flat=True)
        )

        await self.send(text_data=json.dumps({
            'taken_seats': taken_seats
        }))

    async def update_seats(self, event):
        await self.send_seat_status()