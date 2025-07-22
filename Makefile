.PHONY: help install run migrate makemigrations colectstatic test clean

#Переменные
PYTHON = python3
PIP = pip3
MANAGE = $(PYTHON) manage.py

DOCKER_COMPOSE = docker compose
DOCKER_IMAGE_NAME = my_django_app
DOCKER_CONTAINER_NAME = my_django_container


# Цель по умолчанию - показать помощь
help:
	@echo "--------------------------------------------------------"
	@echo "Доступные команды для Django-проекта:"
	@echo "--------------------------------------------------------"
	@echo "  make help           - Показать это сообщение"
	@echo "  make install        - Установить зависимости из requirements.txt"
	@echo "  make run            - Запустить Django-сервер разработки (http://127.0.0.1:8000/)"
	@echo "  make run-port       - Запустить Django-сервер с указанием порта"
	@echo "  make migrate        - Применить миграции базы данных"
	@echo "  make makemigrations - Создать новые миграции"
	@echo "  make collectstatic  - Собрать статические файлы"
	@echo "  make test           - Запустить тесты проекта"
	@echo "  make createsuperuser - Создать нового суперпользователя"
	@echo "  make shell          - Запустить Django shell"
	@echo "  make clean          - Удалить временные файлы (__pycache__, *.pyc)"
	@echo "  make migrate-all    - Создать и применить все миграции"
	@echo "  make deploy         - Пример цели для деплоя (требует настройки)"
	@echo ""
	@echo "--- Docker Commands ---"
	@echo "  make docker-build       - Собрать Docker-образ проекта"
	@echo "  make docker-up          - Запустить контейнеры Docker Compose (в фоновом режиме)"
	@echo "  make docker-up-foreground - Запустить контейнеры Docker Compose (в текущем терминале)"
	@echo "  make docker-down        - Остановить и удалить контейнеры Docker Compose"
	@echo "  make docker-exec CMD=\"...\" - Выполнить произвольную команду в основном контейнере Django"
	@echo "  make docker-migrate     - Применить миграции внутри контейнера"
	@echo "  make docker-makemigrations - Создать миграции внутри контейнера"
	@echo "  make docker-test        - Запустить тесты внутри контейнера"
	@echo "  make docker-shell       - Запустить Django shell внутри контейнера"
	@echo "  make docker-logs        - Просмотр логов контейнеров"
	@echo "  make docker-rm-containers - Удалить все остановленные контейнеры"
	@echo "  make docker-rm-images   - Удалить Docker-образ проекта"
	@echo "--------------------------------------------------------"

#Command

install:
	$(PIP) install -r requirements.txt

run:
	$(MANAGE) runserver

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

colectstatic:
	$(MANAGE) colectstatic --noinput

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm {}+

createsuperuser:
	$(MANAGE) createsuperuser

migrate-all: makemigrations migrate
	echo "Все миграции созданы и применены."


docker-build:
	@echo "Собираем Docker-образ $(DOCKER_IMAGE_NAME)..."
	docker build -t $(DOCKER_IMAGE_NAME) .
	@echo "Docker-образ $(DOCKER_IMAGE_NAME) успешно собран."

run-up:
	@echo "Запускаем Docker-контейнеры через Docker Compose..."
	$(DOCKER_COMPOSE) up -d --build
	@echo "Docker-контейнеры запущены в фоновом режиме."
docker-down:
	@echo "Останавливаем и удаляем Docker-контейнеры..."
	$(DOCKER_COMPOSE) down --remove-orphans
	@echo "Docker-контейнеры остановлены и удалены."

docker-migrate:
	@echo "Применяем миграции в контейнере..."
	$(DOCKER_COMPOSE) exec web $(PYTHON) manage.py migrate
	@echo "Миграции применены в контейнере."

docker-makemigrations:
	@echo "Создаем новые миграции в контейнере..."
	$(DOCKER_COMPOSE) exec web $(PYTHON) manage.py makemigrations
	@echo "Миграции созданы в контейнере."
docker-createsuperuser:
	@echo "Создаем суперпользователя в контейнере..."
	$(DOCKER_COMPOSE) exec web $(PYTHON) manage.py createsuperuser
	@echo "Суперпользователь создан (или процесс запущен) в контейнере."

# Загрузка начальных данных (фиксатур) в контейнере
# Пример: make docker-load-initial-data FIXTURE="my_app/fixtures/initial_data.json"
docker-load-initial-data:
	@echo "Загружаем начальные данные из фиксатуры $(FIXTURE) в контейнере..."
	$(DOCKER_COMPOSE) exec web $(PYTHON) manage.py load_initial_data $(FIXTURE)
	@echo "Начальные данные загружены в контейнере."
docker-collectstatic:
	@echo "Собираем статические файлы в контейнере..."
	$(DOCKER_COMPOSE) exec web $(PYTHON) manage.py collectstatic --noinput
	@echo "Статические файлы собраны в контейнере."

doker-start:docker-makemigrations  docker-migrate docker-createsuperuser docker-load-initial-data docker-collectstatic
	@echo "Миграции созданы в контейнере."

docker-rm-containers:
	@echo "Удаляем все остановленные Docker-контейнеры..."
	docker rm $(shell docker ps -aq) || true
	@echo "Остановленные Docker-контейнеры удалены."