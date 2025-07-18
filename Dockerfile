
FROM python:3.12-slim

#  переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN adduser --disabled-password --gecos '' director
#  рабочая директория
WORKDIR /app

# Зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем проект
COPY . .
# Меняем владельца файлов на нового пользователя
RUN chown -R director:director/app

# Переключаемся на пользователя
USER director
# Добавим команду запуска
CMD ["gunicorn", "cinewave.wsgi:application", "--bind", "0.0.0.0:8000"]