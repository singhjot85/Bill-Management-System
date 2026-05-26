###################################
## Make Targets for normal shell ##
###################################

poetry-run:
	cd backend && poetry run python manage.py runserver

poetry-mm:
	cd backend && poetry run python manage.py makemigrations $(app_name)

poetry-m:
	cd backend && poetry run python manage.py migrate

poetry-superuser:
	cd backend && poetry run python manage.py createsuperuser

poetry-shell-plus:
	cd backend && poetry run python manage.py shell_plus --ipython

setup-system:
	@command -v brew >/dev/null || (echo "Homebrew is required. Install from https://brew.sh"; exit 1)
	brew install poetry cairo pkg-config cmake pango gdk-pixbuf libffi

setup-python:
	cd backend && poetry lock && poetry install --no-interaction

pre-commit:
	cd backend && poetry run pre-commit run --all-files

#####################################
## Make target for docker commands ##
#####################################

COMPOSE_NAME:=compose/compose.local.yaml
BASE_COMPOSE_CMD:=docker compose -f ${COMPOSE_NAME}
DJANGO_CONTAINER_CMD:=${BASE_COMPOSE_CMD} run --rm django

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
	${DJANGO_CONTAINER_CMD} bash
bash: docker-bash

docker-django-makemigrations-empty:
	@echo "⌛ Making an empty migration in App: ➡️[${app}] with Name: ➡️[${mig_name}]..."
	@echo "⚠️ If this was not intended use command with app= or mig_name= flags"
	${DJANGO_CONTAINER_CMD} python manage.py makemigrations --empty ${app} --name ${mig_name}
mme: docker-django-makemigrations-empty

docker-django-makemigrations:
	@echo "⌛ Making migrations in App: ➡️[${app}]..."
	@echo "⚠️ If this was not intended use command with app= flag"
	${DJANGO_CONTAINER_CMD} python manage.py makemigrations ${app}
mm: docker-django-makemigrations

docker-django-migrate:
	@echo "⌛ Migrating Schema's now..."
	${DJANGO_CONTAINER_CMD} python manage.py migrate
m: docker-django-migrate

docker-django-shell:
	@echo "⌛ Launching Django shell..."
	${DJANGO_CONTAINER_CMD} python manage.py shell
s: docker-django-shell

docker-clean-project:
	@echo "☣️ Cleaning entire project: Containers, Volumes, Compose Images, Orphan containers"
	${BASE_COMPOSE_CMD} down --volumes --rmi all --remove-orphans
clean: docker-clean-project

docker-clean-build-run:
	make docker-clean-project
	make build
	make m
	make run
cbr: docker-clean-build-run

docker-clean-local-setup:
	make clean
	make build
	make m
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
	make run
clean-setup: docker-clean-local-setup

docker-rebuild:
	${BASE_COMPOSE_CMD} down
	make build
	make m
	make run
rebuild: docker-rebuild

docker-clean-local-setup-fast:
	${BASE_COMPOSE_CMD} down
	make build
	make m
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
	make run
setup: docker-clean-local-setup-fast

docker-local-db-reset:
	${BASE_COMPOSE_CMD} down --volumes
	make m
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	${DJANGO_CONTAINER_CMD} python manage.py migrate_schemas --shared
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
	make run
db-reset: docker-local-db-reset

docker-django-shell-plus:
	@echo "⌛ Launching Django shell-plus..."
	${DJANGO_CONTAINER_CMD} python manage.py shell_plus --ipython
sp: docker-django-shell-plus

.PHONY:
	build
	run
	bash
	mme
	mm
	m
	s
	sp
	clean
	cbr
	clean-setup
	setup
	db-reset
	rebuild
