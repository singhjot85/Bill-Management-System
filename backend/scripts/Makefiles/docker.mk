# Default variable values, will be overriden in main project Markdown
BASE_COMPOSE_CMD:=docker compose -f ../compose/compose.local.yaml
DJANGO_CONTAINER_CMD:=&& docker compose -f ../compose/compose.local.yaml run --rm django

TEST_DIR:=tests/
TEST_FILTER:=""

app:=setup
schema_name:=public
emn:=default_empty_migration
make_migrations:=false

#####################################
## Make target for docker commands ##
#####################################


.PHONY: build, rebuild, clean, cbr, run, run-d
# -----
# Builds, Destroys, Runs
# -----

docker-build:
	@echo "⌛ Starting build process..."
	@echo "⚠️ This stage might pull images make sure you are connected"
	${BASE_COMPOSE_CMD} build
build: docker-build

docker-rebuild:
	@echo "⌛ Putting down containers build process..."
	${BASE_COMPOSE_CMD} down
	make build
	make run
rebuild: docker-rebuild

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

docker-run:
	@echo "⌛ Starting containers..."
	${BASE_COMPOSE_CMD} up
run: docker-run

docker-detached-run:
	@echo "⌛ Starting containers..."
	${BASE_COMPOSE_CMD} up -d
run-d: docker-detached-run


.PHONY: mm, m, mme, bash, s, sp, ts, tsp
# -----
# Migrations and Shells
# -----

docker-django-makemigrations:
	@echo "⌛ Making migrations in App: ➡️[${app}]..."
	@echo "⚠️ If this was not intended use command with app= flag"
	${DJANGO_CONTAINER_CMD} python manage.py makemigrations ${app}
mm: docker-django-makemigrations

docker-django-migrate:
	@echo "⌛ Migrating Schema's now..."
	${DJANGO_CONTAINER_CMD} python manage.py migrate
m: docker-django-migrate

docker-django-makemigrations-empty:
	@echo "⌛ Making an empty migration in App: ➡️[${app}] with Name: ➡️[${emn}]..."
	@echo "⚠️ If this was not intended use command with 'app=' or 'emn=' flags"
	${DJANGO_CONTAINER_CMD} python manage.py makemigrations --empty ${app} --name ${emn}
mme: docker-django-makemigrations-empty

docker-django-bash:
	@echo "⌛ Starting bash in Django container..."
	${DJANGO_CONTAINER_CMD} bash
bash: docker-django-bash

docker-django-shell:
	@echo "⌛ Launching Django shell..."
	${DJANGO_CONTAINER_CMD} python manage.py shell
s: docker-django-shell

docker-django-tenants-shell:
	@echo "⌛ Launching django-tenants shell..."
	${DJANGO_CONTAINER_CMD} python manage.py tenant_command shell
ts: docker-django-tenants-shell

docker-django-shell-plus:
	@echo "⌛ Launching Django shell-plus..."
	${DJANGO_CONTAINER_CMD} python manage.py shell_plus --ipython
sp: docker-django-shell-plus

docker-django-shell-plus:
	@echo "⌛ Launching Django shell-plus..."
	${DJANGO_CONTAINER_CMD} python manage.py tenant_command shell_plus --ipython
tsp: docker-django-shell-plus


.PHONY: clean-light-setup, setup, dev-setup, db-reset, run-seeder, clean-setup
# -----
# Setup and Resets
# -----

docker-clean-light-setup:
	make clean
	make build
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
	make run
clean-light-setup: docker-clean-light-setup

docker-clean-setup:
	make clean
	make build
	${DJANGO_CONTAINER_CMD} python manage.py run_seeder
clean-setup: docker-clean-setup

docker-run-seeder:
	${DJANGO_CONTAINER_CMD} python manage.py run_seeder
run-seeder: docker-run-seeder

docker-clean-local-setup-fast:
	${BASE_COMPOSE_CMD} down
	make build
	make m
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
	make run
setup: docker-clean-local-setup-fast

docker-dev-setup:
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_tenants
	make m
	${DJANGO_CONTAINER_CMD} python manage.py bootstrap_users
dev-setup: docker-dev-setup

docker-local-db-reset:
	${BASE_COMPOSE_CMD} down --volumes
	if [ "${make_migrations}" = "true" ]; then make mm; fi
db-reset: docker-local-db-reset


.PHONY: t, tf, docker-service-state-check,
# -----
# Testing and Debugging
# -----
docker-test:
	@echo "⌛ Running tests in container..."
	${DJANGO_CONTAINER_CMD} pytest
t: docker-test

docker-test-filter:
	@echo "⌛ Running tests in container..."
	$(DJANGO_CONTAINER_CMD) pytest $(TEST_DIR) $(if $(TEST_FILTER),-k $(TEST_FILTER))
tf: docker-test-filter

docker-service-state-check:
	${BASE_COMPOSE_CMD} ps --format json | jq -s 'map({service: .Service, status: .State})'
