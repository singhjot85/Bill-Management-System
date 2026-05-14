#!/bin/bash
set -e

# TODO: Figure out a better way to do this
# echo "Running shared schema migrations..."
# python manage.py migrate_schemas --shared --noinput

# echo "Running tenant migrations..."
# python manage.py migrate_schemas --noinput

echo "Executing command..."
exec "$@"
