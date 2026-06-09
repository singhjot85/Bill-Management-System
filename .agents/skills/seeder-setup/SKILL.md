---
name: seeder-setup
description: Manage and create seeders for local data required during development. Use when user asks to "seed data", "create seeder", or "setup local data".
---

# Seeder Setup Skill

This skill provides procedures and guidance for managing the local data seeding system in the Bill Management Application (BMA).

## Quick Actions

| Task | Command |
| :--- | :--- |
| **Seed All Data** | `make setup` or `bash scripts/seeder.sh all` |
| **Seed Tenants** | `bash scripts/seeder.sh tenants` |
| **Seed Users** | `bash scripts/seeder.sh users` |
| **Reset Database** | `make db-reset` |

## Core Architecture

The seeder system follows the **Template Method Pattern**:
- **`BaseSeeder`**: Defines the lifecycle (`run()`) and common utilities like `filter_model_fields` and `load_data`.
- **Concrete Seeders**: Implement the `seed()` method to handle specific model logic.
- **Data Location**: All seed data is stored as JSON in `project_apps/setup/local_setup/data/`.

## Procedures

### 1. Running Seeders
To run seeders, use the provided `make` targets or management commands via Docker:
```bash
docker-compose -f compose/local/compose.yaml run --rm django python manage.py bootstrap_tenants
docker-compose -f compose/local/compose.yaml run --rm django python manage.py bootstrap_users
```

### 2. Creating a New Seeder
To add a new seeder to the system:
1. **Define the Seeder Class**: Create a new file in `project_apps/setup/local_setup/seeders/` (e.g., `invoice_seeder.py`).
2. **Inherit from `BaseSeeder`**:
   ```python
   class InvoiceSeeder(BaseSeeder):
       label = "Invoice Seeder"
       def seed(self, *args, **kwargs):
           # Your seeding logic here
           pass
   ```
3. **Add to Runner**: Update `project_apps/setup/local_setup/runner.py` to include your new seeder in the execution flow.
4. **Prepare Data**: Create a corresponding JSON file in `project_apps/setup/local_setup/data/`.

### 3. Modifying Existing Data
Edit the JSON files in `project_apps/setup/local_setup/data/` to update default users, tenants, or branding information. The seeders are designed to be idempotent where possible (using `get_or_create`).

## Resources
- **Base Seeder**: `project_apps/setup/local_setup/seeders/base_seeder.py`
- **Data Directory**: `project_apps/setup/local_setup/data/`
- **Documentation**: `documentation/Local_Setup.md`
- **Helper Script**: `.gemini/skills/seeder-setup/scripts/seeder.sh`
