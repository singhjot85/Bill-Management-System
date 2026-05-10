# GEMINI Context: Bill Management System

Comprehensive context for the Bill Management System (BMA), a multi-tenant Django application for invoice generation and payment management.

## Project Overview
The BMA allows vendors (tenants) to manage customers, generate invoices, and process payments via Razorpay. It supports public users (unauthenticated checkout), private users (authenticated customers), tenant admins, and platform admins.

### Tech Stack
- **Backend**: Django 5.2, Django REST Framework (DRF), `django-tenants` (Multi-tenancy), Celery + Valkey (Async tasks), `xhtml2pdf`/`weasyprint` (PDF Generation).
- **Frontend**: Vue 3 + Vite (API-driven), Django Templates (Legacy/Server-side rendering).
- **Database**: PostgreSQL (Schema-per-tenant architecture).
- **Infrastructure**: Docker, Compose, Poetry (Dependency management).

---

## Architecture & Conventions

### Multi-Tenancy (`django-tenants`)
- **Public Schema**: Contains `auth`, `tenants`, and platform-wide configurations.
- **Tenant Schema**: Contains `customer_management`, `payments_management`.
- All tenant-specific models must support multi-tenant isolation.
- **Models**: Use `BetterModelMixin` (UUID keys + Soft Delete + Timestamps).

### Service Layer (`project_apps/services`)
To avoid direct API calls and maintain separation of concerns, the project uses a three-tier service architecture:
1. **Base HTTP Service (`base.py`)**: A generalized wrapper around `requests.Session` for all external API calls.
2. **Specific Services (`razorpay_service.py`)**: Encapsulates external provider logic (e.g., Razorpay signature verification, order creation).
3. **Orchestration Layer (`payment_orchestrator.py`)**: Coordinates between services and Django models using atomic transactions (`@transaction.atomic`) and race-condition protection (`select_for_update()`).

### Payment Verification Rules
- **Atomicity**: `Payment` and `Invoice` status updates must happen in a single transaction.
- **Verification**: Must include `verified_on`, `verified_by`, and `is_verified` together.
- **Signatures**: Never store or log raw API secrets; use HMAC-SHA256 for local signature verification.

---

## Building and Running

### System Dependencies
Requires `brew install cairo pango gdk-pixbuf libffi pkg-config cmake`.

### Local Development (Poetry)
- **Install**: `make setup` (runs `poetry lock` and `poetry install`).
- **Run Server**: `make poetry-run` (`python manage.py runserver`).
- **Migrations**: `make poetry-mm app_name=<app>` and `make poetry-m`.
- **Tests**: `poetry run pytest`.

### Docker Environment
- **Build**: `make build`.
- **Run**: `make run`.
- **Clean Setup**: `make clean-setup` (Builds, bootstraps tenants/users, and runs).
- **Shell**: `make bash`.

---

## Development Conventions

### Coding Standards
- **Linting/Formatting**: Uses `black` and `isort`. Pre-commit hooks are configured (`.pre-commit-config.yaml`).
- **Imports**: Follows `isort` profile `black`.
- **Models**: Inherit from `project_apps.utils.BetterModelMixin` for standard fields (UUID, created, modified, deleted).

### Testing
- **Suite**: `pytest` with `pytest-django`.
- **Isolation**: Multi-tenant isolation tests are required for new features.
- **Mocking**: Use `unittest.mock` to avoid external API calls during tests.

### API Rules
- Serializers in `serializers.py`, ViewSets in `views.py`.
- Prefer `Action` decorators for custom workflows in ViewSets.
- ViewSets should consume Service Layers for complex business logic.

### Frontend Generalization & Configuration
To support multi-tenancy and highly customizable vendor branding, the frontend follows a strict **Configuration-Driven Architecture**.

#### 1. Component Hierarchy
- **Layouts** (e.g., `TenantHomePage.vue`): Persistent wrappers (Navbar/Footer) that orchestrate configuration and manage routing via `<router-view>`.
- **Smart Components** (e.g., `HomePage.vue`, `AuthPage.vue`, `DonatePage.vue`): High-level views that consume sections of the configuration to build complex, dynamic layouts.
- **Dumb Components** (e.g., `Navbar.vue`, `PRStub.vue`): Atomic, reusable UI elements. They are logic-agnostic, configurable via props, and communicate with parents via events.

#### 2. Configuration & Styling Standards (`tenantConfig.ts`)
- **Centralized Source**: All view-related configurations reside in `frontend/src/config/tenantConfig.ts`.
- **Order-Based Layouts**: Use `order` arrays (e.g., `order: ['image', 'title', 'text']`) to allow vendors to reposition elements without code changes.
- **Resolver Pattern**: For dynamic content (e.g., theme-toggle icons or tenant names), use a string-to-function mapping. Components reference a "resolver" name in their config, and the component resolves it at runtime.
- **Generic View Props**: Layouts pass configurations to children via `<router-view v-slot="{ Component }"> <component :is="Component" :config="viewConfig" /> </router-view>`.
- **Styling Mandate**: **ALWAYS use CSS variables** for all styling (colors, spacing, typography, effects). Avoid hardcoded values in components. Use existing variables from `variables.css` and extend it as needed. Prefer Vanilla CSS over TailwindCSS.

#### 3. Event-Driven Decoupling
- Components must **EMIT** actions (`@action`, `@navigate`) rather than handling routing or state mutations internally.
- The parent Layout or Smart component is responsible for handling these emits (e.g., `router.push`, `store.toggleTheme`).
- This keeps the UI components pure, testable, and reusable across different business contexts.

---

## Key Files & Directories
- `config/`: Project configuration, routers, and environment variables.
- `project_apps/services/`: Central logic for external integrations and orchestration.
- `project_apps/utils/`: Common mixins and utility functions.
- `documentation/`: Detailed architecture specs (e.g., `Razorpay_Integration_Spec.md`).
- `compose/`: Docker configuration files.

---

## Documentation Conventions
- ALWAYS document any new enhancement and infra change.
- Documentation lies in `documentation/`
- For Infra Setups also include simple and crisp mermaids.
- Mermaid diagrams should be simple, if the functionality is complex, split the diawgram.