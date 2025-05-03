install:
	uv sync

dev:
	uv run python manage.py runserver

req-txt:
	uv pip compile pyproject.toml -o requirements.txt

#_______________________________________________________________________________Lint

lint:
	uv run ruff check .

fix:
	uv run ruff check --fix
