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

build:
	./build.sh

render-start:
	gunicorn task_manager.wsgi

#_______________________________________________________________________________

ms:
	django-admin makemessages -l ru

cm:
	django-admin compilemessages