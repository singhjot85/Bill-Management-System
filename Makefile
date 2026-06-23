include backend/scripts/Makefiles/docker.mk
include backend/scripts/Makefiles/raw.mk

COMPOSE_NAME:=compose/compose.local.yaml
BASE_COMPOSE_CMD:=docker compose -f ${COMPOSE_NAME}
DJANGO_CONTAINER_CMD:=${BASE_COMPOSE_CMD} run --rm django

BACKEND_DIR=backend

default_target_app:=setup
default_target_schema:=public
deafult_empty_migration_name:=default_empty_migration

app?=$(default_target_app)
emn?=$(deafult_empty_migration_name)
schema_name?=$(default_target_schema)
