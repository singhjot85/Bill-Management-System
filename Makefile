.PHONY: build run setup setup-system setup-python

poetry-run:
	poetry run python manage.py runserver

poetry-mm:
	poetry run python manage.py makemigrations $(app_name)

poetry-m:
	poetry run python manage.py migrate

poetry-superuser:
	poetry run python manage.py createsuperuser

poetry-shell-plus:
	poetry run python manage.py shell_plus --ipython

setup-system:
	@command -v brew >/dev/null || (echo "Homebrew is required. Install from https://brew.sh"; exit 1)
	brew install poetry cairo pkg-config cmake pango gdk-pixbuf libffi

setup-python:
	poetry lock
	poetry install --no-interaction

setup: setup-system setup-python

COMPOSE_NAME:=compose/local/compose.yaml

BASE_COMPOSE_CMD:=docker compose -f ${COMPOSE_NAME}

docker-build:
	${BASE_COMPOSE_CMD} build
build: docker-build

docker-run:
	${BASE_COMPOSE_CMD} up
run: docker-run

docker-bash:
	${BASE_COMPOSE_CMD} run --rm django bash
bash: docker-bash