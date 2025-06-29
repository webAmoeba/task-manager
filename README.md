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
```