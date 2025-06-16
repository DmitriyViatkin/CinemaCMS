import os
import django
from django.conf import settings
from datetime import datetime, timezone # Додаємо timezone для коректних дат

# --- ВАЖЛИВО: ЗМІНІТЬ 'cinewave.settings' НА НАЗВУ ВАШОГО ПРОЕКТУ ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinewave.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from faker import Faker
import random

# Отримуємо вашу кастомну модель User
User = get_user_model()

# Ініціалізуємо Faker для генерації даних (українська локаль)
fake = Faker('uk_UA')

num_users_to_create = 100
sql_statements = []

# Отримуємо назву таблиці для вашої моделі User
# Зазвичай це '<назва_додатку>_user', наприклад, 'users_user' або 'auth_user'
# Перевірте у вашій базі даних, як називається таблиця!
user_table_name = User._meta.db_table

# Стосунки Many-to-Many (groups, user_permissions) не обробляються цим INSERT
# Якщо вам потрібні ці зв'язки, їх доведеться додавати окремими INSERT-ами в auth_user_groups/auth_user_user_permissions

# Заголовки стовпців для INSERT INTO
columns = [
    "username", "password", "email", "first_name", "last_name",
    "is_superuser", "is_staff", "is_active", "date_joined", "last_login",
    "city", "address", "languages", "phone_number", "gender", "date_of_birth"
]

# Вибираємо варіанти з ваших CHOICES
gender_choices_values = [choice[0] for choice in User.GENDER_CHOICES]
languages_choices_values = [choice[0] for choice in User.LANGUAGES_CHOICES]

print(f"Генерація {num_users_to_create} SQL INSERT запитів...")

for i in range(num_users_to_create):
    # Генерація унікального username
    username_base = fake.user_name()
    username = f"{username_base}{random.randint(1000, 9999)}"
    # Проста перевірка на унікальність серед генерованих, не перевіряє БД
    while any(f"'{username}'" in s for s in sql_statements):
        username = f"{username_base}{random.randint(1000, 9999)}"

    email = fake.email()
    raw_password = 'testpassword123' # Пароль для всіх тестових користувачів
    hashed_password = make_password(raw_password) # Хешуємо пароль за допомогою Django!

    # Стандартні поля AbstractUser
    first_name = fake.first_name()
    last_name = fake.last_name()
    is_superuser = 'FALSE'
    is_staff = 'FALSE'
    is_active = 'TRUE'
    # date_joined та last_login у форматі ISO 8601 з таймзоною UTC
    now_utc = datetime.now(timezone.utc)
    date_joined = now_utc.isoformat(timespec='milliseconds')
    last_login = 'NULL' # Залишаємо NULL, бо користувач ще не входив

    # Ваші кастомні поля
    city = fake.city()
    address = fake.address()
    languages = random.choice(languages_choices_values)
    phone_number = fake.phone_number()[:15]
    gender = random.choice(gender_choices_values)
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat() # Формат YYYY-MM-DD

    # Допоміжна функція для екранування значень та обробки NULL
    def escape_sql_value(value):
        if value is None or value == 'NULL':
            return 'NULL'
        return f"'{str(value).replace("'", "''")}'"

    values = [
        escape_sql_value(username),
        escape_sql_value(hashed_password),
        escape_sql_value(email),
        escape_sql_value(first_name),
        escape_sql_value(last_name),
        is_superuser,
        is_staff,
        is_active,
        escape_sql_value(date_joined),
        last_login,
        escape_sql_value(city),
        escape_sql_value(address),
        escape_sql_value(languages),
        escape_sql_value(phone_number),
        escape_sql_value(gender),
        escape_sql_value(date_of_birth)
    ]

    sql = f"INSERT INTO {user_table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
    sql_statements.append(sql)

# Зберігаємо SQL-запити у файл
output_filename = "insert_100_test_users.sql"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_statements))

print(f"\nЗгенеровано {num_users_to_create} SQL INSERT запитів у файл: {output_filename}")
print(f"Зверніть увагу, пароль для всіх користувачів: '{raw_password}'")
print("\nТепер ви можете виконати цей файл у PGAdmin4, psql або іншому інструменті для роботи з PostgreSQL.")
print("Не забудьте оновити послідовність ID після вставки (див. інструкції нижче)!")