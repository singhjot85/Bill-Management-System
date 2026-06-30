---
name: seeder-setup
description: Manage and create seeders for local data required during development. Use when user asks to "seed data", "create seeder", or "setup local data".
---

# Seeder Setup Skill

This skill provides procedures and guidance for managing the local data seeding system in the Bill Management Application (BMA).
The seeder architecture can be found under [Seeder Architecture](../../../docs/operations/seeding.md)

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
2. **Analysis:** Before adding a new seeder get answer(s) to these questions:
   - Will this data be seeded in production, or only for local development.
   - What are the possible trigger's:
     - Management Commands
     - run_seeder Management Command, -> run's all the seeders.
     - Admin Action.
     - Internally through code.
   - What all model fields are to be seeded and what all are to be random fields.
    > Do not assume anything, analyse the requirement and prompt the user whenever you face any confusion or complex choice.

- Now every seeder inherits from [`BaseSeeder`](../../../backend/apps/setup/local_setup/seeders/base_seeder.py).
- A simple new seeder implementation might look like:

```python
class SeederName(BaseSeeder):
    label: str = "Seeder Label for logging"
    REGISTERY_KEY: str = "only if seeder needs to be registered"

    def run_in_schema(self) -> str:
        return "Tenant Schema Name where seeder needs to run"

    def seed(self, *args, **kwargs):
        # Fetch data from json file
        # Either use the object cached data or use load_file(...)

        # Use create_object(...) to create an object
        ...
```

3. **Add to Runner**: Update `project_apps/setup/local_setup/runner.py` to include your new seeder in the execution flow.
4. **Prepare Data**: Create a corresponding JSON file in `project_apps/setup/local_setup/data/`, or add to existing json_data if new tenant is not being created.

### 3. Modifying Existing Data

Edit the JSON files in `project_apps/setup/local_setup/data/` to update default users, tenants, or branding information. The seeders are designed to be idempotent where possible (using `get_or_create`).

## Resources

- **Base Seeder**: `project_apps/setup/local_setup/seeders/base_seeder.py`
- **Data Directory**: `project_apps/setup/local_setup/data/`
- **Documentation**: `docs/operations/seeding.md`
- **Helper Script**: `.gemini/skills/seeder-setup/scripts/seeder.sh`
