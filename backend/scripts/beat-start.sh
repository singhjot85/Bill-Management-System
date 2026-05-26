#!/bin/sh

set -e

echo "Starting Celery Beat..."
exec celery -A backend.config.celery beat --loglevel=info
