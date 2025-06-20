import json
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import Halls, Seats

@receiver(post_save, sender=Halls)
def process_hall_scheme_from_file_only(sender, instance, created, **kwargs):
    print(f"--- Сигнал process_hall_scheme_from_file_only: HALL ID {instance.id}, created: {created} ---")

    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ: Используем seats_set вместо seats_in_hall ---
    instance.seats_set.all().delete()
    print(f"--- Удалены существующие места для зала ID {instance.id} ---")

    scheme_file = instance.scheme_hall

    # --- Главная логика: попытка обработать схему из загруженного JSON-файла ---
    if scheme_file and scheme_file.name.endswith('.json'):
        try:
            with scheme_file.open('r', encoding='utf-8') as f:
                scheme_data = json.load(f)

            if isinstance(scheme_data, (dict, list)):
                print(f"--- Обработка схемы зала '{instance.title}' из файла '{scheme_file.name}' ---")

                # Логика создания Seats из файла
                if isinstance(scheme_data, list): # Если JSON - это массив залов
                    for hall_data in scheme_data:
                        # Ищем текущий зал по названию. Это может быть проблемой, если названия залов не уникальны.
                        # Лучше бы сопоставлять по ID, но если схема общая, то по названию.
                        if hall_data.get('name') == instance.title:
                            _create_seats_from_json_dict(instance, hall_data)
                            break # Схема найдена и обработана, выходим из цикла
                elif isinstance(scheme_data, dict): # Если JSON - это один объект зала
                    _create_seats_from_json_dict(instance, scheme_data)

            else:
                print(f"Предупреждение: Файл '{scheme_file.name}' для зала '{instance.title}' содержит неверный формат JSON (ожидается объект или массив).")

        except FileNotFoundError:
            print(f" Ошибка: Файл схемы '{scheme_file.name}' для зала '{instance.title}' не найден.")
        except json.JSONDecodeError as e:
            print(f" Ошибка JSON: Файл '{scheme_file.name}' для зала '{instance.title}' не является действительным JSON: {e}")
        except Exception as e:
            print(f"Общая ошибка при обработке схемы зала '{instance.title}' (ID: {instance.pk}) из файла '{scheme_file.name}': {e}")

    elif scheme_file and not scheme_file.name.endswith('.json'):
        print(f"Предупреждение: Загруженный файл '{scheme_file.name}' для зала '{instance.title}' не является JSON-файлом. Схема не будет обработана.")
    else:
        print(f"--- Для зала ID {instance.id} файл схемы не загружен или поле 'scheme_hall' пусто. Места не создаются. ---")

def _create_seats_from_json_dict(hall_instance, scheme_dict):
    seats_to_create = []
    for row_data in scheme_dict.get('rows', []):
        row_number = row_data.get('row_number')
        if row_number is None:
            print(f"Предупреждение: В JSON-схеме для зала '{hall_instance.title}' в ряду отсутствует 'row_number': {row_data}")
            continue

        for seat_data in row_data.get('seats', []):
            seat_number = seat_data.get('seat_number')
            if seat_number is None:
                print(f"Предупреждение: В JSON-схеме для зала '{hall_instance.title}' в месте отсутствует 'seat_number': {seat_data}")
                continue

            is_vip = seat_data.get('is_vip', False)
            price = seat_data.get('price', 120.00)

            if is_vip and price == 120.00:
                price = 200.00

            seats_to_create.append(
                Seats(
                    halls=hall_instance,
                    number_row=row_number,
                    seat=seat_number,
                    date=date.today(), # Здесь вы устанавливаете текущую дату
                    status=seat_data.get('status', 'F'),
                    is_vip=is_vip,
                    price=price,
                )
            )
    if seats_to_create:
        Seats.objects.bulk_create(seats_to_create)
        print(f"--- Создано {len(seats_to_create)} мест для зала ID {hall_instance.id} из файла схемы ---")