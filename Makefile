install:
	uv sync

dev:
	uv run python manage.py runserver

req:
	uv pip compile pyproject.toml -o requirements.txt

#_______________________________________________________________________________Lint

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix

#_______________________________________________________________________________

collectstatic:
	python manage.py collectstatic --noinput

migrate:
	python manage.py migrate
	python manage.py shell < create_superuser.py

dev-migrate:
	uv run manage.py makemigrations
	uv run manage.py migrate

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi

#_______________________________________________________________________________Translate

ms:
	django-admin makemessages -l ru

cm:
	django-admin compilemessages

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