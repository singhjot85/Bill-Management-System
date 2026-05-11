---
name: docker-dev
description: Manage local Docker development environment. Use when user asks to "start Docker", "setup dev environment", "check logs", or "open container shell".
---

# Docker Development

When active:
1. Setup: `bash scripts/docker_dev.sh setup`
2. Start: `bash scripts/docker_dev.sh start`
3. Status: `bash scripts/docker_dev.sh status`
4. Logs: `bash scripts/docker_dev.sh logs [service]`

Services: web (8000), frontend (3000), db (5432), valkey (6379)
Django hot-reloads; Celery requires restart on task changes
