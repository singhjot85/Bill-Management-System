#!/bin/bash

set -e

# Netcat can be missused, avoid it, instead use compose builtin healthcheck
# echo "Waiting for Broker..."
# while ! nc -z bma_broker 6378; do
#   sleep 0.1
# done

echo "Starting Celery Worker..."
exec celery -A config.celery worker --loglevel=info --concurrency=4
