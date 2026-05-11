---
name: migration-management
description: Run and inspect database migrations across schemas. Use when user asks to "migrate database", "check migrations", or "run migrations".
---

# Migration Management

When active:
1. Check: `bash scripts/manage_migrations.sh check`
2. All schemas: `bash scripts/manage_migrations.sh migrate-all`
3. Single tenant: `bash scripts/manage_migrations.sh migrate-tenant <schema>`
4. Never skip migrations; test on staging first
