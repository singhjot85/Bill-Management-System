include backend/scripts/Makefiles/docker.mk
include backend/scripts/Makefiles/raw.mk

COMPOSE_PATH:=compose/compose.local.yaml
DEBUGPY_COMPOSE_PATH:=compose/compose.debugpy.yml

BASE_COMPOSE_CMD:=docker compose -f ${COMPOSE_PATH}
DEBUGPY_COMPOSE_CMD:=docker compose -f ${COMPOSE_PATH} -f ${DEBUGPY_COMPOSE_PATH}

DJANGO_CONTAINER_CMD:=${BASE_COMPOSE_CMD} run --rm django

BACKEND_DIR=backend
TEST_DIR:=tests/
TEST_FILTER:=""

default_target_app:=setup
default_target_schema:=public
deafult_empty_migration_name:=default_empty_migration

app?=$(default_target_app)
emn?=$(deafult_empty_migration_name)
schema_name?=$(default_target_schema)
