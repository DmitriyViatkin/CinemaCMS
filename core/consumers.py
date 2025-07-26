import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Импортируйте все необходимые модели
from core.models import Tickets, Sessions, Seats  # Убедитесь, что Sessions и Seats импортированы


class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"session_{self.session_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Отправить начальный статус при подключении клиента
        await self.send_full_seat_status()  # Изменено имя функции для ясности

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'refresh':
            await self.send_full_seat_status()  # Изменено имя функции для ясности

    # Этот метод будет получать все статусы мест и отправлять их
    async def send_full_seat_status(self):
        # Используем sync_to_async для операций ORM
        updated_seats_data = await sync_to_async(self._get_current_seat_statuses)()

        await self.send(text_data=json.dumps({
            'updated_seats': updated_seats_data  # <-- Ключ изменен на 'updated_seats'
        }))

    # Этот метод вызывается, когда сообщение отправляется в группу слоя каналов
    async def update_seats(self, event):
        # При покупке/бронировании, повторно получить и отправить полный статус
        await self.send_full_seat_status()

    # Синхронный вспомогательный метод для получения данных о местах из базы данных
    def _get_current_seat_statuses(self):
        try:
            session = Sessions.objects.select_related('hall_id').get(pk=self.session_id)
            hall = session.hall_id

            hall_seats = Seats.objects.filter(halls=hall).order_by('number_row', 'seat')

            # Получить ID всех мест, которые связаны с билетом для этого сеанса
            occupied_ticket_seat_ids = Tickets.objects.filter(session=session).values_list('seat__id', flat=True)
            occupied_ticket_seat_ids = set(occupied_ticket_seat_ids)  # Используем set для более быстрого поиска

            # Получить ID мест, принадлежащих текущему пользователю (если контекст пользователя доступен в consumer)
            # ВАЖНО: Consumer не может легко получить 'request.user' напрямую из представления.
            # Если вам нужно отправлять статус 'U' из consumer, вам придется передавать ID пользователя
            # в сообщении слоя каналов или обрабатывать статус 'U' чисто на стороне клиента на основе первоначальной загрузки.
            # Пока что мы будем считать, что 'U' обрабатывается первоначальной загрузкой клиента.
            # Для обновлений WebSocket более важны статусы 'S' (продано/занято) и 'b' (забронировано).
            # Поэтому мы пометим как 'S' или 'b', если билет существует, независимо от того, кому он принадлежит.

            user_tickets_seat_ids_for_this_consumer = []
            if self.scope['user'].is_authenticated:
                user_tickets_seat_ids_for_this_consumer = list(Tickets.objects.filter(
                    session=session,
                    profile=self.scope['user']
                ).values_list('seat__id', flat=True))

            updated_seats_list = []
            for seat in hall_seats:
                current_display_status = seat.status  # Получаем базовый статус места из модели Seats

                is_occupied_by_any_ticket = (seat.id in occupied_ticket_seat_ids)
                is_user_ticket_for_this_consumer = (seat.id in user_tickets_seat_ids_for_this_consumer)

                # Определяем статус для отправки клиенту
                if is_user_ticket_for_this_consumer:
                    # Если этот конкретный пользователь владеет билетом на это место, пометить его как 'U'
                    display_status = "U"
                elif is_occupied_by_any_ticket:
                    # Если для этого сеанса и места существует какой-либо билет
                    # Если базовый статус был 'F' (Свободно), но теперь занят билетом, установить 'S' (Продано)
                    # В противном случае, сохранить статус из БД ('b' для забронированного, 'S' для проданного, 'N' для недоступного)
                    if seat.status == 'F':
                        display_status = 'S'  # По умолчанию 'Продано/Занято', если был создан новый билет
                    else:
                        display_status = seat.status  # Сохранить 'S', 'b' или 'N', если уже установлено в БД
                else:
                    # Если билета нет, использовать базовый статус места (например, 'F' или 'N')
                    display_status = seat.status

                updated_seats_list.append({
                    'seat_id': str(seat.id),  # Убедитесь, что seat_id является строкой, как ожидается JS dataset
                    'status': display_status,  # Отправляем определенный статус отображения
                    # Вы также можете захотеть отправить цену/VIP-статус, если они динамические и нужны для обновлений клиента:
                    # 'is_vip': seat.is_vip,
                    # 'price': float(seat.price or session.price), # Использование цены сеанса в качестве запасного варианта
                })
            return updated_seats_list
        except Sessions.DoesNotExist:
            print(f"Сеанс с ID {self.session_id} не найден в consumer.")
            return []
        except Exception as e:
            print(f"Ошибка при получении статусов мест в consumer: {e}")
            return []