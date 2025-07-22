FROM python:3.12-slim

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Создаем пользователя director
RUN adduser --disabled-password --gecos '' director

# Рабочая директория
WORKDIR /app

# Зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем проект
COPY . .

# Меняем владельца файлов на нового пользователя
RUN chown -R director:director /app

# Переключаемся на пользователя director для всех последующих операций
USER director
