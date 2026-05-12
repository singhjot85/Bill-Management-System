###################################
## Make Targets for normal shell ##
###################################

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

#####################################
## Make target for docker commands ##
#####################################

COMPOSE_NAME:=compose/local/compose.yaml
BASE_COMPOSE_CMD:=docker compose -f ${COMPOSE_NAME}
BASE_DJANGO_CONTAINER:=${BASE_COMPOSE_CMD} run --rm django

app:=setup
mig_name:=default_empty_migration
schem_name:=localclient

docker-build:
	@echo "⌛ Starting build process..."
	@echo "⚠️ This stage might pull images make sure you are connected"
	${BASE_COMPOSE_CMD} build
build: docker-build

docker-run:
	@echo "⌛ Starting containers..."
	${BASE_COMPOSE_CMD} up
run: docker-run

docker-bash:
	@echo "⌛ Starting bash in containers..."
	${BASE_DJANGO_CONTAINER} bash
bash: docker-bash

docker-django-makemigrations-empty:
	@echo "⌛ Making an empty migration in App: ➡️[${app}] with Name: ➡️[${mig_name}]..."
	@echo "⚠️ If this was not intended use command with app= or mig_name= flags"
	${BASE_DJANGO_CONTAINER} python manage.py makemigrations --empty ${app} --name ${mig_name}
mme: docker-django-makemigrations-empty

docker-django-makemigrations:
	@echo "⌛ Making migrations in App: ➡️[${app}]..."
	@echo "⚠️ If this was not intended use command with app= flag"
	${BASE_DJANGO_CONTAINER} python manage.py makemigrations ${app}
mm: docker-django-makemigrations

docker-django-migrate:
	@echo "⌛ Migrating Schema's now..."
	${BASE_DJANGO_CONTAINER} python manage.py migrate
m: docker-django-migrate

docker-django-shell:
	@echo "⌛ Launching Django shell..."
	${BASE_DJANGO_CONTAINER} python manage.py shell
s: docker-django-shell

docker-clean-project:
	@echo "☣️ Cleaning entire project: Containers, Volumes, Compose Images, Orphan containers"
	${BASE_COMPOSE_CMD} down --volumes --rmi all --remove-orphans
clean: docker-clean-project

docker-clean-build-run:
	make docker-clean-project
	make build
	make run
cbr: docker-clean-build-run

docker-clean-local-setup:
	make clean
	make build
	${BASE_DJANGO_CONTAINER} python manage.py bootstrap_tenants --schema_name localclient
	${BASE_DJANGO_CONTAINER} python manage.py bootstrap_users
	make run
clean-setup: docker-clean-local-setup

.PHONY:
	build
	run
	setup setup-system setup-python
	bash s
	mme mm m
	clean cbr
	clean-setup
