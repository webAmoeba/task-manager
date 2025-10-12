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