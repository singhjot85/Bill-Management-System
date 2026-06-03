#####################################
## Make target for docker commands ##
#####################################

docker-build:
	@echo "⌛ Starting build process..."
	@echo "⚠️ This stage might pull images make sure you are connected"
	${BASE_COMPOSE_CMD} build
build: docker-build

docker-run:
	@echo "⌛ Starting containers..."
	${BASE_COMPOSE_CMD} up
run: docker-run

docker-django-bash:
	@echo "⌛ Starting bash in Django container..."
	${DJANGO_CONTAINER_CMD} bash
bash: docker-django-bash

docker-django-makemigrations-empty:
	@echo "⌛ Making an empty migration in App: ➡️[${app}] with Name: ➡️[${emn}]..."
	@echo "⚠️ If this was not intended use command with 'app=' or 'emn=' flags"
	${DJANGO_CONTAINER_CMD} python manage.py makemigrations --empty ${app} --name ${emn}
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
	make clean
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
	@echo "⌛ Putting down containers build process..."
	${BASE_COMPOSE_CMD} down
	make build
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

docker-dev-setup:
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	make m
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
dev-setup: docker-dev-setup

docker-django-shell-plus:
	@echo "⌛ Launching Django shell-plus..."
	${DJANGO_CONTAINER_CMD} python manage.py shell_plus --ipython
sp: docker-django-shell-plus

docker-test:
	@echo "⌛ Running tests in container..."
	${DJANGO_CONTAINER_CMD} pytest
test: docker-test

.PHONY: build run bash s sp m mm mme cbr clean rebuild setup clean-setup db-reset docker-test test dev-setup



docker-service-state-check:
	${BASE_COMPOSE_CMD} ps --format json | jq -s 'map({service: .Service, status: .State})'

docker-detached-run:
	@echo "⌛ Starting containers..."
	${BASE_COMPOSE_CMD} up -d

.PHONY: docker-service-state-check docker-detached-run
