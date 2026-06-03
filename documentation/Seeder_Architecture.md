# Local Setup for BMA
Being a configurable app, BMA needs some tenant's and configurations to be pre-setup for local testing and development

**Location:** `backend/apps/setup/local_setup`

## Diectory Structure:
```
backend/apps/setup/local_setup/
|- __init__.py
|- runner.py                # The Orchestrator ( "core python file")
|- guards.py                # Environment safety checks
|- seeders/
|   |- __init__.py
|   |- base.py              # Base Seeder class
|   |- tenant_seeder.py     # Seeder for tenants and branding
|   |- user_seeder.py       # Seeder for users
|- data/
|   |- tenant_public.json   # Public tenant data
|   |- tenant_ngosite.json  # NGO tenant data
|   |- tenant_restrauntsite.json # Restaurant tenant data
```

## The Seeder Pattern (LLD Concept: Template Method Pattern)
- Each seeder follows a contract defined in `BaseSeeder`.
- Seeders are initialized with a JSON filename from the `data/` directory.
- Every seeder implements `seed()`, while the base class handles logging and lifecycle via `run()`.
- Data is loaded from JSON files, allowing for easy configuration of tenants, branding, and users.

## The Orchestrator (LLD Concept: Chain of Responsibility + Facade)
- `SEEDER_PIPELINE` is explicit dependency-ordered list. This is the Facade Pattern - the caller *(management command, admin action, whoever)* just calls `run_local_setup()` and doesn't need to know the internals.
- The alternative here would be auto-discovery (scan the seeders/ directory and run everything found). That's more dynamic but removes explicit ordering control - dangerous when you have FK dependencies. Explicit is better here.

## The Guard (LLD Concept: Precondition / Design by Contract)
- This is Design by Contract - the function advertises a precondition and enforces it. The caller doesn't have to remember to check, the function protects itself.

## The Open-Source Safety Angle
- Since this is open-source, the data/sample_data.py file is critical. All seed data - *tenant names, sample customer emails, dummy API keys* - should live there and be obviously fake.
