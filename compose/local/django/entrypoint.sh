#!/bin/bash
set -e

echo "Creating Shared Schema..."
python manage.py migrate_schemas --shared --noinput

echo "Creating Default Private Schemas..."
python manage.py bootstrap_tenant

# echo "Collecting Static Content..."
#python manage.py collectstatic

echo "Starting Server now..."
python manage.py runserver

exec "$@"