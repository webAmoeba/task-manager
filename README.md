### Hexlet tests and linter status:
[![Actions Status](https://github.com/webAmoeba/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/webAmoeba/python-project-52/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=webAmoeba_python-project-52&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=webAmoeba_python-project-52)

## Deployed:
[🌎 task-manager.webamoeba.ru/](https://task-manager.webamoeba.ru/)

# Task Manager:
Welcome to the Task Manager project! This repository contains a web application built with Django that allows users to manage tasks efficiently by creating, updating, assigning, and organizing them with labels and statuses. It supports user authentication, role-based permissions, and detailed task tracking.

## Requirements:
To run this project, you need to have the following software installed:
- Python >=3.10
- Uv
- Redis server (for Channels and Celery)

## Preparation:
Create .env file with code kind of:
```bash
webserver=127.0.0.1

DEBUG=True

SECRET_KEY=secret_key
DATABASE_URL=sqlite:///database_name.db

DJANGO_SUPERUSER_USERNAME=superuser
DJANGO_SUPERUSER_EMAIL=superuser@example.com
DJANGO_SUPERUSER_PASSWORD=password

rollbar_token=rollbar_token
CHANNEL_USE_IN_MEMORY=0
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
CELERY_TASK_ALWAYS_EAGER=1
CELERY_TASK_EAGER_PROPAGATES=1
```

## Installation:
To set up the project, navigate to the project directory and run the following commands:
```bash
make install
```
```bash
make migrate
```

## Local run:
```bash
make dev
# in separate terminals
make celery-worker
make celery-beat
# or run everything in one terminal
# (press Ctrl+C to stop all processes)
make dev-all
```

## Telegram bot
1. Create the bot via BotFather and add the token to `.env` as `TELEGRAM_BOT_TOKEN`.
2. Generate a personal access token on the `/telegram/` page after logging in.
3. Run the bot locally:
   ```bash
   make bot
   ```
4. In Telegram, send the generated token to the bot and use commands like `/tasks`, `/complete <id>`, `/notifications`.

## API
- Obtain a token via `POST /api/auth/token/` with `username` and `password`.
- Use the token in requests: `Authorization: Token <token>`.
- Task endpoints available at `/api/tasks/` (CRUD + `POST /api/tasks/{id}/complete/`).
