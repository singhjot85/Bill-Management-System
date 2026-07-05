---
title: Seeder Architecture (Seeder 2.0)
type: operation
app: core
last_updated: 2026-06-30
tags: [seeding, setup, local-development, automation, django-tenants]
---

# Seeder Architecture (Seeder 2.0)

BMA's seeding architecture ensures idempotent, predictable, and schema-isolated data provisioning across local development environments. It separates data loading strategies from database creation patterns, automatically resolves dependencies via topological sorting, and tracks execution states across multi-tenant schemas.

## Directory Structure

Seeders are located in `backend/apps/setup/seeder/`:
- `runner.py`: The Orchestrator/Facade that sorts the pipeline and runs seeders across schemas.
- `registry.py`: The explicit seeder pipeline list (`SEEDER_PIPELINE`).
- `base.py`: The `BaseSeeder` template method class, `Scope` definitions, and `ObjectCreationMixin` for de-duplicated model initialization.
- `sources.py`: The `DataSource` strategy interfaces (`FixtureSource`, `TenantAwareFixtureSource`, `FactorySource`).
- `exceptions.py`: Custom seeder-related exception classes.
- `seeders/`: Individual concrete seeder classes (e.g., `tenant_seeder.py`, `user_seeder.py`).

The seed data JSON files remain in `backend/apps/setup/local_setup/data/`.

## Key Patterns & Design Decisions

### 1. Template Method Pattern (`BaseSeeder`)
Every seeder inherits from `BaseSeeder`.
- `seed()`: Primitive abstract method overridden by subclasses to implement custom seeding logic.
- `run()`: The invariant skeleton method that manages the transaction lifecycle, checks if execution is already marked successful, and updates the `SeederExecutionLog` model inside the correct schema context.

### 2. Strategy Pattern (`DataSource`)
The seeder delegates data fetching to a pluggable `DataSource` strategy:
- `FixtureSource`: Loads JSON data from single or multiple paths.
- `TenantAwareFixtureSource`: Dynamically resolves the source JSON file depending on the current active schema name (e.g., `public`, `localngo`, `localrestraunt`).
- `FactorySource`: Generates mock records programmatically using FactoryBoy factories.

### 3. Topological Sorting (Kahn's Algorithm)
Seeders declare their direct dependencies using the `depends_on` list class attribute. The runner (`runner.py`) uses Kahn's algorithm to resolve these dependencies dynamically into a Directed Acyclic Graph (DAG) execution sequence before running them, preventing foreign key constraint violations.

### 4. Database-Backed Idempotency
Seeder runs are tracked in the `SeederExecutionLog` table, provisioned in both public and private tenant schemas. This permits independent tracking and prevents redundant execution. By default, database checks query the raw `_base_manager` to safely bypass soft-delete logic.

### 5. Multi-Tenant Scoping
Seeders specify a `scope` attribute:
- `Scope.PUBLIC`: Executed exactly once within the `public` schema database context.
- `Scope.PER_TENANT`: Executed once for each tenant schema context configured in the database.

## Usage

Trigger the full seeder pipeline using the Django management command:
```bash
python manage.py run_seeder
```

To run a specific seeder only (and any other seeders it requires based on the dependency graph):
```bash
python manage.py run_seeder --seeder-name TenantSeeder
```

---

## Related Documents
- [Architectural Overview](../architecture/overview.md)
- [Multi-Tenancy Architecture](../architecture/multi-tenancy.md)
- [Data Modeling](../architecture/data-models.md)
