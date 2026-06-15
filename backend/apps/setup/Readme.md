# Setup Module (BMA)

The `setup` module is a core infrastructural component of the Bill Management System (BMA). It handles system-wide configurations, multi-tenant initialization, and automated data seeding for local development and testing environments.

## 1. Architectural Flow

The module operates through two primary layers:

### A. Dynamic Configuration Layer
The `Configurations` model (in `models.py`) provides a versioned, cached interface for system settings (e.g., UI branding, notification templates).
1. **Request**: A service or view requests a configuration via `Configurations.get_latest_config(interface_type)`.
2. **Cache Check**: The system checks Valkey (cache) using a schema-specific key (`{schema_name}:{interface_type}`).
3. **Database Fallback**: If not cached, it retrieves the latest versioned record from the database.
4. **Serialization**: The `details` JSON field is returned, providing dynamic behavior to the frontend and backend.

### B. Local Setup & Seeding Layer
The `local_setup` sub-module handles the bootstrapping of the application environment.
1. **Trigger**: Initiated via management commands (`bootstrap_tenants`, `bootstrap_users`) or the `run_local_setup` orchestrator.
2. **Guard Check**: `guards.py` ensures seeding only runs in `DEBUG` mode and approved local environments.
3. **Orchestration**: `runner.py` iterates through a pipeline of seeders defined in `seeders/`.
4. **Execution**: Each seeder loads data from `local_setup/data/*.json` and performs idempotent database operations.

## 2. Design Patterns

| Pattern | Implementation |
| :--- | :--- |
| **Template Method** | `BaseSeeder` defines the `run()` lifecycle (logging, transactions) while subclasses implement the `seed()` logic. |
| **Facade** | `runner.py` provides a simple interface (`run_local_setup`) to hide the complexity of multiple seeders and data files. |
| **Singleton/Cache** | `Configurations` model implements a caching strategy to minimize database hits for frequently accessed settings. |
| **Strategy** | Different seeders (`TenantSeeder`, `UserSeeder`) encapsulate specific seeding logic for different domain models. |
| **Design by Contract** | `guards.py` enforces preconditions (e.g., `is_local_env`) before sensitive setup operations proceed. |

## 3. Developer Guide

### Adding a New Configuration Type
1. Add a new choice to `ConfigurationInterfaceChoices` in `constants.py`.
2. Create a migration if necessary (though the model uses a flexible `JSONField`).
3. Use `Configurations.objects.create(interface_type='...', details={...})` to add data.

### Extending Seeders
To add a new seeder:
1. Create a new file in `local_setup/seeders/` inheriting from `BaseSeeder`.
2. Implement the `seed()` method with idempotent logic (use `get_or_create`).
3. Register the seeder in `local_setup/runner.py` within the appropriate bootstrap function.
4. Add corresponding JSON data in `local_setup/data/`.

### Running Setup Commands
```bash
# Bootstrap everything (Tenants, Domains, Branding, Users)
python manage.py bootstrap_tenants
python manage.py bootstrap_users
```

## 4. Directory Structure

```text
backend/apps/setup/
├── fixtures/             # Default Django fixtures for initial migrations.
├── local_setup/          # Core logic for environment bootstrapping.
│   ├── data/             # JSON datasets for tenants, users, and configs.
│   ├── seeders/          # Specialized classes for seeding different models.
│   ├── guards.py         # Safety checks (prevents production wipes).
│   ├── runner.py         # The orchestrator for local setup.
├── management/           # Django management commands.
│   └── commands/         # CLI tools (bootstrap_tenants, etc.).
├── constants.py          # Enums for configuration types.
├── models.py             # Configurations model with versioning and caching.
```

## 5. Operational Guardrails

- **Environment Safety**: Seeders **MUST** check `is_local_env()` to prevent accidental data injection in production.
- **Idempotency**: All seeding logic must be re-runnable without creating duplicate records or failing (use `filter_model_fields` and `get_or_create`).
- **Multi-Tenancy**: 
    - `TenantSeeder` operates on the `public` schema to create tenants.
    - `UserSeeder` creates users in the `public` schema.
    - `Configurations` can exist in both `public` and `tenant` schemas depending on the `interface_type`.
- **Atomic Transactions**: The `BaseSeeder.run()` method wraps executions in `transaction.atomic()` to ensure database integrity.
