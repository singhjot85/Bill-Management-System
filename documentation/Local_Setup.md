# Local Setup for BMA
Being a configurable app, BMA needs some tenant's and configurations to be pre-setup for local testing and development

**Location:** `project_apps/setup/local_setup`

## Diectory Structure:
```
project_apps/setup/local_setup/
|- __init__.py
|- runner.py                # The Orchestrator ( "core python file")
|- guards.py                # Environment safety checks
|- seeders/
|   |- __init__.py
|   |- tenant_seeder.py
|   |- customer_seeder.py
|   |- invoice_seeder.py
|   |- config_seeder.py     # For Configurations model in setup app
|- data/
|   |- sample_data.py       # Centralized seed data constants (NOT hardcoded in seeders)
```

## The Seeder Pattern (LLD Concept: Template Method Pattern)
- Each seeder should follows a contract defined in `BaseSeeder`.
- Every seeder implements `seed()`, the base class handles the logging ceremony via `run()`. 
- This is the Template Method Pattern - the invariant steps *(logging, lifecycle)* live in the base, the variant step *(seed)* is delegated.

## The Orchestrator (LLD Concept: Chain of Responsibility + Facade)
- `SEEDER_PIPELINE` is explicit dependency-ordered list. This is the Facade Pattern - the caller *(management command, admin action, whoever)* just calls `run_local_setup()` and doesn't need to know the internals.
- The alternative here would be auto-discovery (scan the seeders/ directory and run everything found). That's more dynamic but removes explicit ordering control - dangerous when you have FK dependencies. Explicit is better here.

## The Guard (LLD Concept: Precondition / Design by Contract)
- This is Design by Contract - the function advertises a precondition and enforces it. The caller doesn't have to remember to check, the function protects itself.

## The Open-Source Safety Angle
- Since this is open-source, the data/sample_data.py file is critical. All seed data - *tenant names, sample customer emails, dummy API keys* - should live there and be obviously fake.