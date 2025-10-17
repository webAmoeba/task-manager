.PHONY: install req dev dev-django makemigrations migrate dev-migrate collectstatic \
        superuser build render-start celery-worker celery-beat dev-all \
        bot kill-all lint fix test test-cov cover-html test-users test-statuses ms cm \
        vps-update vps-services-restart vps-status vps-logs vps-update-web-only vps-reload-nginx

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

# --- VPS deploy --------------------------------------------------------------

# Переопределяйте при запуске: make vps-update BRANCH=main WEB_SVC=... WORKER_SVC=...
BRANCH ?= main
# Defaults for your current VPS setup: only web unit is present.
# You can override any of these at call time: make vps-update WEB_SVC=...
WEB_SVC ?= task_manager.service
WORKER_SVC ?= /bin/true
BEAT_SVC ?= /bin/true
BOT_SVC ?= /bin/true

vps-update:
	@set -e; \
	echo ">> Fetch + reset to origin/$(BRANCH)"; \
	git fetch origin --prune; \
	git checkout -q $(BRANCH) || true; \
	git reset --hard origin/$(BRANCH); \
	echo ">> Sync deps (locked)"; \
	if ! uv sync --all-groups --locked; then \
        echo ">> Locked sync failed; fallback to uv sync"; \
        uv sync --all-groups; \
	fi; \
	echo ">> Migrate DB"; \
	uv run python manage.py migrate --noinput; \
	echo ">> Collect static"; \
	uv run python manage.py collectstatic --noinput; \
	$(MAKE) vps-services-restart

vps-services-restart:
	@set -e; \
	echo ">> Restart services"; \
	sudo systemctl restart $(WEB_SVC); \
	if [ -n "$(WORKER_SVC)" ] && systemctl list-unit-files | grep -q "^$(WORKER_SVC)"; then \
	    sudo systemctl restart $(WORKER_SVC); \
	else echo "skip worker ($(WORKER_SVC))"; fi; \
	if [ -n "$(BEAT_SVC)" ] && systemctl list-unit-files | grep -q "^$(BEAT_SVC)"; then \
	    sudo systemctl restart $(BEAT_SVC); \
	else echo "skip beat ($(BEAT_SVC))"; fi; \
	if [ -n "$(BOT_SVC)" ] && systemctl list-unit-files | grep -q "^$(BOT_SVC)"; then \
	    sudo systemctl restart $(BOT_SVC); \
	else echo "skip bot ($(BOT_SVC))"; fi; \
	echo "OK"

vps-status:
	@echo "== Systemd status =="; \
	sudo systemctl --no-pager status $(WEB_SVC) || true; \
	if [ -n "$(WORKER_SVC)" ]; then sudo systemctl --no-pager status $(WORKER_SVC) || true; fi; \
	if [ -n "$(BEAT_SVC)" ]; then sudo systemctl --no-pager status $(BEAT_SVC) || true; fi; \
	if [ -n "$(BOT_SVC)" ]; then sudo systemctl --no-pager status $(BOT_SVC) || true; fi

vps-logs:
	@echo "Ctrl+C to stop following logs"; \
	sudo journalctl -u $(WEB_SVC) \
	$(if $(WORKER_SVC),-u $(WORKER_SVC),) \
	$(if $(BEAT_SVC),-u $(BEAT_SVC),) \
	$(if $(BOT_SVC),-u $(BOT_SVC),) -f || true

vps-update-web-only:
	$(MAKE) vps-update WORKER_SVC= BEAT_SVC= BOT_SVC=

vps-reload-nginx:
	sudo nginx -t && sudo systemctl reload nginx

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
