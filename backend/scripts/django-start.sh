#!/bin/bash
set -e

echo "Starting django service..."
python backend/manage.py runserver 0.0.0.0:8000
