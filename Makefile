.PHONY: install req dev dev-django makemigrations migrate dev-migrate collectstatic \
        superuser build render-start celery-worker celery-beat dev-all \
        bot kill-all lint fix test test-cov cover-html test-users test-statuses ms cm

install:
	uv sync

req:
	uv pip compile pyproject.toml -o requirements.txt

dev:
	uv run python -m daphne -p 8000 task_manager.asgi:application

dev-django:
	uv run python manage.py runserver

# --- Миграции / база ---------------------------------------------------------

makemigrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

dev-migrate: makemigrations migrate

collectstatic:
	uv run python manage.py collectstatic --noinput

superuser:
	uv run python manage.py shell < create_superuser.py

# --- Celery / служебные процессы ---------------------------------------------

celery-worker:
	uv run celery -A task_manager worker -l info

celery-beat:
	uv run celery -A task_manager beat -l info

dev-all:
	@trap 'kill $$daphne $$worker $$beat $$bot 2>/dev/null' INT TERM EXIT; \
	uv run python -m daphne -p 8000 task_manager.asgi:application & daphne=$$!; \
	uv run celery -A task_manager worker -l info & worker=$$!; \
	uv run celery -A task_manager beat -l info & beat=$$!; \
	bot=; \
	if [ -z "$$TELEGRAM_BOT_TOKEN" ]; then \
		echo "TELEGRAM_BOT_TOKEN not exported – bot не запущен"; \
	else \
		uv run python bot/run_bot.py & bot=$$!; \
	fi; \
	if [ -n "$$bot" ]; then \
		wait $$daphne $$worker $$beat $$bot; \
	else \
		wait $$daphne $$worker $$beat; \
	fi

bot:
	uv run python bot/run_bot.py

kill-all:
	pkill -f "celery -A task_manager" || true
	pkill -f "python -m daphne -p 8000 task_manager.asgi:application" || true
	pkill -f "bot/run_bot.py" || true
	pkill -f "manage.py runserver" || true

# --- Сборки и деплой ---------------------------------------------------------

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi

# --- Линт / форматирование ---------------------------------------------------

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix

# --- Локализация -------------------------------------------------------------

ms:
	uv run django-admin makemessages -l ru

cm:
	uv run django-admin compilemessages

cmf: kill-all cm dev-all

# --- Тесты -------------------------------------------------------------------

test:
	uv run pytest

test-cov:
	uv run pytest --cov=task_manager

cover-html:
	uv run pytest --cov=task_manager --cov-report html

test-users:
	uv run manage.py test task_manager.apps.users

test-statuses:
	uv run manage.py test task_manager.apps.statuses
