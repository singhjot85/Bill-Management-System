---
title: Seeder Architecture
type: operation
app: core
last_updated: 2026-06-15
tags: [seeding, setup, local-development, automation]
---

# Seeder Architecture

TL;DR: BMA's seeding architecture ensures idempotent and predictable data provisioning across local and production environments. It uses a pipeline-based approach with explicit dependency ordering and environment safety guards.

This document covers the structure, patterns, and safety mechanisms of the BMA data seeding system.

## Directory Structure
Seeders are located in `backend/apps/setup/local_setup/`:
- `runner.py`: The Orchestrator (Facade).
- `guards.py`: Environment safety checks (Design by Contract).
- `seeders/`: Individual seeder classes (e.g., `tenant_seeder.py`, `user_seeder.py`).
- `data/`: JSON files containing the actual seed data.

## Key Patterns

### 1. Template Method Pattern
Every seeder inherits from a `BaseSeeder` contract.
- `seed()`: Implemented by subclasses to handle specific model logic.
- `run()`: Handled by the base class to provide consistent logging and lifecycle management.

### 2. Facade Pattern (The Orchestrator)
The `SEEDER_PIPELINE` defines an explicit, dependency-ordered list of seeders. Callers simply execute `run_local_setup()`, abstracting away the internal complexity and ensuring Foreign Key dependencies are respected.

### 3. Design by Contract (The Guards)
Guards enforce preconditions (e.g., "only run in local environment") before execution. This prevents accidental data corruption in production environments.

## Safety & Idempotency
- **Fake Data**: All default seed data (tenant names, emails, keys) is explicitly fake and suitable for open-source distribution.
- **Idempotency**: Seeders are designed to be run multiple times without creating duplicate records or inconsistent states (e.g., using `get_or_create`).

## Usage
Seeders can be triggered via management commands or during the initial environment setup to provide a fully functional local development environment.

---

## Related Documents
- [Architectural Overview](../architecture/overview.md)
- [Multi-Tenancy Architecture](../architecture/multi-tenancy.md)
- [Data Modeling](../architecture/data-models.md)
