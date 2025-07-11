import json
import io # Добавьте этот импорт, если его нет
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Halls, Seats # Убедитесь, что импорты правильные

@receiver(post_save, sender=Halls)
def process_hall_scheme_from_file_only(sender, instance, created, **kwargs):
    print(f"--- Сигнал process_hall_scheme_from_file_only: HALL ID {instance.id}, created: {created} ---")

    # ВАЖНО: Мы всегда удаляем старые места при изменении схемы зала
    # Это гарантирует, что схема будет полностью перезаписана
    instance.seats_in_hall.all().delete()
    print(f"--- Удалены существующие места для зала ID {instance.id} ---")

    scheme_file = instance.scheme_hall

    # --- Главная логика: попытка обработать схему из загруженного JSON-файла ---
    if scheme_file and scheme_file.name.endswith('.json'):
        try:
            with scheme_file.open('rb') as f_binary:
                text_stream = io.TextIOWrapper(f_binary, encoding='utf-8')
                scheme_data = json.load(text_stream)

            if isinstance(scheme_data, (dict, list)):
                print(f"--- Обработка схемы зала '{instance.title}' из файла '{scheme_file.name}' ---")

                if isinstance(scheme_data, list):
                    # Если JSON - это список залов, находим нужный по имени
                    for hall_data in scheme_data:
                        if hall_data.get('name') == instance.title:
                            _create_seats_from_json_dict(instance, hall_data)
                            break
                elif isinstance(scheme_data, dict):
                    # Если JSON - это схема одного зала
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


            seats_to_create.append(
                Seats(
                    halls=hall_instance, # Убедитесь, что поле ForeignKey в Seats называется 'halls'
                    number_row=row_number,
                    seat=seat_number,
                    date=date.today(), # Важно: здесь 'date' - это дата создания записи о месте.
                                       # Для сеансов дата будет браться из Session.date.
                                       # Если Seats.date используется для привязки к конкретной дате показа,
                                       # то эту логику нужно будет пересмотреть.
                                       # Сейчас это просто дата создания места в зале.
                    status=seat_data.get('status', 'F'), # Статус по умолчанию 'F' (Free)
                    is_vip=seat_data.get('is_vip', False), # is_vip все еще берется из схемы, это свойство места
                    # --- УДАЛЕНО: Поле price больше не заполняется здесь ---
                    price=None, # Устанавливаем явно None, чтобы база данных использовала default или allow_null=True
                )
            )
    if seats_to_create:
        Seats.objects.bulk_create(seats_to_create)
        print(f"--- Создано {len(seats_to_create)} мест для зала ID {hall_instance.id} из файла схемы ---")
