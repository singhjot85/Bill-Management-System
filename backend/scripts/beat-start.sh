#!/bin/sh

set -e

echo "Starting Celery Beat..."
exec celery -A config.celery beat --loglevel=info
