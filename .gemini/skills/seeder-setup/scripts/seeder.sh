#!/bin/bash

# Helper script for seeder management
# Usage: ./seeder.sh [command]

COMMAND=$1
COMPOSE_FILE="compose/local/compose.yaml"
DJANGO_RUN="docker-compose -f $COMPOSE_FILE run --rm django"

case $COMMAND in
    "tenants")
        echo "Seeding tenants..."
        $DJANGO_RUN python manage.py bootstrap_tenants
        ;;
    "users")
        echo "Seeding users..."
        $DJANGO_RUN python manage.py bootstrap_users
        ;;
    "all")
        echo "Running all seeders..."
        $DJANGO_RUN python manage.py bootstrap_tenants
        $DJANGO_RUN python manage.py bootstrap_users
        ;;
    "create")
        echo "To create a new seeder:"
        echo "1. Define seeder class in project_apps/setup/local_setup/seeders/"
        echo "2. Inherit from BaseSeeder and implement seed()"
        echo "3. Add seeder to project_apps/setup/local_setup/runner.py"
        echo "4. Create JSON data file in project_apps/setup/local_setup/data/"
        ;;
    *)
        echo "Usage: $0 {tenants|users|all|create}"
        exit 1
        ;;
esac
