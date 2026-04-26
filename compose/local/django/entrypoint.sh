#!/bin/bash
set -e

echo "Running shared schema migrations..."
python manage.py migrate_schemas --shared --noinput

echo "Running tenant migrations..."
python manage.py migrate --noinput

echo "Executing command..."
exec "$@"