install:
	uv sync

dev-django:
	uv run python manage.py runserver

dev:
	uv run python -m daphne -p 8000 task_manager.asgi:application

req:
	uv pip compile pyproject.toml -o requirements.txt

#_______________________________________________________________________________Lint

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix

#_______________________________________________________________________________

collectstatic:
	uv run python manage.py collectstatic --noinput

superuser:
	uv run python manage.py shell < create_superuser.py

makemigrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

dev-migrate: makemigrations migrate

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi

celery-worker:
	uv run celery -A task_manager worker -l info

celery-beat:
	uv run celery -A task_manager beat -l info

dev-all:
	@trap 'kill $$daphne $$worker $$beat 2>/dev/null' INT TERM EXIT; \
	uv run python -m daphne -p 8000 task_manager.asgi:application & daphne=$$!; \
	uv run celery -A task_manager worker -l info & worker=$$!; \
	uv run celery -A task_manager beat -l info & beat=$$!; \
	wait $$daphne $$worker $$beat

bot:
	uv run python bot/run_bot.py



#_______________________________________________________________________________Translate

ms:
	uv run django-admin makemessages -l ru

cm:
	uv run django-admin compilemessages

#_______________________________________________________________________________Test
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
