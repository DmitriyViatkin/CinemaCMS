FROM python:3.12-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем пользователя director
RUN adduser --disabled-password --gecos '' director

# Рабочая директория
WORKDIR /app

# Устанавливаем локали и необходимые системные зависимости для psycopg2
RUN apt-get update && apt-get install -y locales libpq-dev gcc \
    && sed -i -e 's/# uk_UA.UTF-8 UTF-8/uk_UA.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменные окружения для локали
ENV LANG uk_UA.UTF-8
ENV LANGUAGE uk_UA:uk
ENV LC_ALL uk_UA.UTF-8

# Копируем requirements.txt и устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем проект
COPY . .

# Меняем владельца файлов на нового пользователя
RUN chown -R director:director /app

# Переключаемся на пользователя director для всех последующих операций
USER director
