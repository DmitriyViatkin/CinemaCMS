from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Sessions, Seats, Halls
from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from core.models import Halls, Seats  # заміни шлях на актуальний

@receiver(post_save, sender=Halls)
def create_seats_for_hall(sender, instance, created, **kwargs):
    print(f"--- Сигнал create_seats_for_hall: HALL ID {instance.id}, created: {created} ---")
    if created:
        print(f"--- Створення місць для залу '{instance.title}' ---")

        if instance.rows and instance.seats_row and instance.rows > 0 and instance.seats_row > 0:
            last_row = instance.rows
            seats_list_to_create = []

            for row in range(1, instance.rows + 1):
                for seat_num in range(1, instance.seats_row + 1):
                    is_vip = (row == last_row)
                    price = 200.00 if is_vip else 120.00

                    seats_list_to_create.append(
                        Seats(
                            halls=instance,
                            number_row=row,
                            seat=seat_num,
                            date=date.today(),
                            status='F',
                            is_vip=is_vip,
                            price=price,

                        )
                    )
            if seats_list_to_create:
                Seats.objects.bulk_create(seats_list_to_create)
                print(f"--- Створено {len(seats_list_to_create)} місць у залі ID {instance.id} ---")
            else:
                print(f"--- Список місць пустий для залу ID {instance.id} ---")
        else:
            print(f"--- Невірні параметри залу (rows / seats_row) для ID {instance.id} ---")
    else:
        print(f"--- Зал ID {instance.id} оновлений, місця не створюються ---")