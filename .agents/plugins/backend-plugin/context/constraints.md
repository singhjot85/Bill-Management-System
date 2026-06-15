# Backend Plugin — Constraints Context

This file defines hard boundaries the subagents must never cross, regardless of
what the feature request says. These are not style preferences — they are
architectural invariants of the BMA project.

`context_builder.py` injects this file in FULL for every subagent invocation,
at every stage. There are no stage or agent filters here — constraints are always active.

---

## Injection Instruction for `context_builder.py`

```yaml
required: hard_stop
reason: >
  Constraints are non-negotiable. If this file is missing, no subagent
  should be invoked. The system has no safety boundaries without it.
inject_for_stages:
  - ALL
inject_for_agents:
  - ALL
inject_as: >
  Prepend to every subagent prompt under the header:
  === CONSTRAINTS: Non-negotiable project boundaries ===
```

---

## 1. Multi-Tenancy Invariants

**Source:** `docs/architecture/async-system.md`, `backend/Readme.md`

These constraints exist because BMA uses `django-tenants` with schema-per-tenant
isolation. Violating them causes data leakage across tenants — a silent, catastrophic bug.

- Never query tenant-scoped models without an active schema context. Always verify
  `connection.schema_name` is not `'public'` before executing tenant-scoped queries.
- Never pass model instances across async task boundaries. Always pass IDs and
  schema names. Reconstruct inside the task using `schema_context`.
- Never auto-inject schema in a Beat coordinator task. Beat runs in public schema.
  Coordinators must fan out explicitly using `TenantFanOut`.
- Never horizontally scale a Beat container. It is a singleton by design.

---

## 2. Async Task Invariants

**Source:** `docs/architecture/async-system.md`

- Every task that touches external systems or produces side effects must have an
  idempotency guard. No exceptions.
- Always classify task failure mode at declaration time: `SILENT`, `ALERT`, or `DLQ`.
  Never leave failure_mode unset (it defaults to SILENT, which hides real failures).
- Never store model instances in task kwargs. Only primitive types and IDs.
- Use `select_for_update()` when a task writes to a record that another task or
  request could concurrently modify.
- Task names must be declared in `apps/tasks/registry.py`. Never use auto-generated
  names — they break Beat schedules and DLQ entries when files are moved.

---

## 3. API and View Invariants

**Source:** `backend/Readme.md`

- Never expose raw exception messages in API responses. Always use custom error classes.
- Never bypass DRF serializers. All data in and out of views must be serialized.
- Never expose list endpoints without pagination.
- Always override unused ModelViewSet methods to block unintended access.
- Never define URLs inside individual apps. All URL registration happens in
  `backend/config/routers.py` (tenant) or `backend/config/public_routers.py` (public).
- Always use `DefaultRouter` — never `SimpleRouter`. API root must not be exposed
  in production.

---

## 4. Settings and Configuration Invariants

**Source:** `backend/Readme.md`

- Never hardcode values that vary between environments. Use `variables.py`.
- Never put runtime logic in `settings.py`. Logic goes in `resolvers.py`.
- Never serve static assets from Django in production. Static serving is external.
- Tenant URL config and Public URL config must remain in separate files at all times.

---

## 5. Data Model Invariants

**Source:** `docs/architecture/data-models.md`

- All models must use UUID primary keys. Never use auto-incrementing integer IDs.
- All models must implement `created_at`, `updated_at`, and `is_deleted` (soft delete).
  Never hard-delete records — use soft delete.
- Never store sensitive configuration values in model fields directly. Use the
  `Configurations` model with a `details` JSONField, keyed by `interface_type`.
- Never introduce a new app without discussing it first. New models go into the most
  relevant existing app unless there is a strong architectural reason for a new app.

---

## 6. Dependency Invariants

- Never add a new Python dependency without a corresponding update to `pyproject.toml`
  via Poetry. Never use `pip install` directly.
- Never introduce a new Docker service without a corresponding update to the relevant
  `compose/` file.
- Never add a dependency that duplicates functionality already in the stack.
  Check the existing tech stack in `docs/architecture/overview.md` before proposing anything new.

---

## 7. Rollback Safety Invariants

- Never run `git reset` or `git clean` autonomously.
- Always append touched files to `plugin_state.json → files_touched` before modifying them.
  If a file is touched but not recorded, rollback is unsafe.
- Never modify files outside `backend/` during a backend-plugin session unless
  explicitly declared in the feature's `inter_plugin_contracts`.
