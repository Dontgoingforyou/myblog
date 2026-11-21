# Подъём всего стенда одной командой: make up
# Остановка: make down. Данные базы в volume остаются.
# Нужен заполненный .env в корне.
# Команда собирает образ сайта и запускает PostgreSQL и Django.
# Сайт: http://127.0.0.1:8000/blog/

VENV=my_env
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
COMPOSE=docker compose

.PHONY: help install lint test up down logs migrate seed

help:
	@echo "Команды:"
	@echo "  make install   — создать my_env и поставить зависимости"
	@echo "  make lint      — flake8"
	@echo "  make test      — pytest (нужна запущенная PostgreSQL)"
	@echo "  make up        — собрать и поднять сайт и базу"
	@echo "  make down      — остановить контейнеры, volume базы сохранить"
	@echo "  make logs      — логи стенда"
	@echo "  make migrate   — миграции в уже запущенном контейнере сайта"
	@echo "  make seed      — недостающие примеры, уже написанные посты не меняет"

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

lint:
	$(VENV)/bin/flake8 myblog

test:
	$(PY) -m pytest

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

migrate:
	$(COMPOSE) exec web python myblog/manage.py migrate --noinput

seed:
	cd myblog && ../$(PY) manage.py seed
