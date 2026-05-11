# Docker Compose Setup
Services: web, worker, beat, db, valkey, frontend
Volumes: ./:/app (hot-reload), postgres_data, valkey_data
Ports: 8000 (Django), 3000 (Vue), 5432 (PostgreSQL), 6379 (Valkey)
