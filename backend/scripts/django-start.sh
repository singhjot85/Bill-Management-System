#!/bin/bash
set -e

echo "Debuuging >>> "
ls -lrta

echo "Starting django service..."
python manage.py runserver 0.0.0.0:8000
