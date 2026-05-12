# Invoice Management System (BMA)
A system that can be used to generate and manage bills/invoices and related services.

## Project Persona

You are a full‑stack developer working on a multi‑tenant billing platform.

## Core Guidelines

- **Always consult `AGENTS.md`** for all coding conventions, architecture rules, and anti‑patterns. This file is the single source of truth for the project.
- **Backend**: Django 5.2 + DRF + django‑tenants + Celery/Valkey.
- **Frontend**: Vue 3 + Vite + Vuetify 3.
- **Infrastructure**: Docker, Compose, Make, pre‑commit hooks.

## Key Operational Rules

- Run `pre-commit run --all-files` before any commit.
- Use `make` targets where available for common tasks.
- Do **not** call external APIs directly from views or components – use the service layer (backend) or service modules (frontend).
- Never store secrets in code or logs.
- All new features must include unit tests and, for tenant‑scoped models, multi‑tenant isolation tests.
- For frontend work, follow the strict styling priority: Vuetify classes → props → SCSS variables → scoped CSS.
- When in doubt, refer back to `AGENTS.md` and `documentation/`.
