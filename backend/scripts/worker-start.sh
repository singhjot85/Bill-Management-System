#!/bin/bash

set -e


echo "Starting Celery Worker..."
exec celery -A config.celery worker --loglevel=info --concurrency=4
