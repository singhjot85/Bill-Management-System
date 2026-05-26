# AGENTS.md — Invoice Management System (BMA)

> Complete developer reference for the multi‑tenant billing platform.
> Backend: Django 5.2 + DRF + django‑tenants · Frontend: Vue 3 + Vite + Vuetify 3
> Always consult this file first. For deeper rationale, see `README.md` and `documentation/`.

## 1. Project Overview

- **Purpose**: Multi‑vendor invoicing and payment collection via Razorpay.
- **Users**: Public (unauthenticated checkout), Private (authenticated customers), Tenant Admins, Platform Admins.
- **Tenant architecture**: Shared `public` schema (users, tenants) + isolated tenant schemas.
- **Async tasks**: Celery + Valkey (previously Redis) for PDF generation, email, etc.

## 2. Global Conventions

### Code Quality

- **Formatter**: `black`
- **Import sort**: `isort` (profile `black`)
- **Linting**: pre‑commit hooks configured (see `.pre-commit-config.yaml`) — run `pre-commit run --all-files` before pushing.
- **Testing**: `pytest` + `pytest-django`. Mock all external API calls with `unittest.mock`.
- **Documentation**: Every new feature/infra change must be documented in `documentation/`. For infrastructure include a simple Mermaid diagram; split complex flows into multiple diagrams.

### Key Directories

```
backend/apps/services/ # All external API + orchestration logic
config/ # Django settings, routers, env
documentation/ # Specs, architecture decisions, diagrams
compose/ # Docker Compose files (local & prod)
frontend/ # Vue 3 SPA (API‑driven, built with Vite)
templates/ # Legacy Django templates (keep stable, prefer Vue for new features)
```

## 3. Backend Rules (Django)

### Multi‑Tenancy (`django-tenants`)

- **Public schema**: `auth`, `tenants` models, platform‑wide settings.
- **Tenant schemas**: `customer_management`, `payments_management`.
- **All tenant‑scoped models** must guarantee isolation. Use `BetterModelMixin` from `backend.apps.utils` (provides `uuid` PK, `created`, `modified`, `deleted` — soft‑delete enabled).

### Service Layer (strict separation)

1. **`backend/apps/services/base.py`** — Generic HTTP wrapper (using `requests.Session`). All external calls go through here.
2. **Specific services** (e.g., `razorpay_service.py`) — encapsulate 3rd‑party logic (signature verification, order creation).
3. **Orchestration** (e.g., `payment_orchestrator.py`) — coordinates services and Django models using:
   - `@transaction.atomic` for data consistency.
   - `select_for_update()` to avoid race conditions.

### Payment Verification Rules

- Payment and Invoice status updates **must** run in a single atomic transaction.
- Mandatory fields when marking verified: `verified_on`, `verified_by`, `is_verified`.
- **Never store/sign raw API secrets**. Use HMAC‑SHA256 for local signature checks.

### API Design

- ViewSets in `views.py`, serializers in `serializers.py`.
- Prefer `@action` decorators for custom endpoints.
- **ViewSets consume Service/Orchestration layers** — never call external APIs or complex business logic directly from a view.

### Models & Utilities

- Always inherit from `BetterModelMixin`.
- Add multi‑tenant isolation tests for any new model that is tenant‑scoped.

## 4. Frontend Rules (Vue 3 + Vite + Vuetify)

> **Source code**: `frontend/`
> Full architecture: `frontend/README.md`

### Stack & Tooling

- Vue 3 (Composition API, `<script setup>` syntax)
- Vuetify 3 (Material Design 3), Vite, Pinia, Vue Router 4
- Axios (wrapped in service modules)
- CSS priority: design tokens → Vuetify utility classes → SCSS variables → scoped CSS

### Folder Boundaries (Never cross)

```
frontend/src/
├── assets/ # CSS variables, static files (avoid images where possible)
├── components/
│ ├── common/ # App‑agnostic, dumb UI pieces (AppButton, AppCard …)
│ ├── layout/ # Structural blocks combining common components (HeroSection, TieredItems …)
│ └── view/ # Only for view‑specific overrides (e.g., complex forms). Grouped by view name.
├── config/
│ ├── types/ # TypeScript interfaces for component configs
│ └── defaults/ # Default configs (prevents empty UI before backend data arrives)
├── layouts/ # Root layout shells (TenantLayout, PublicLayout …)
├── router/ # index.ts (logic) + route files (public.ts, private.ts)
├── services/ # ONLY place for HTTP calls (import axios instance from api.js)
├── stores/ # Pinia stores – no direct API calls, just orchestration + reactivity
└── views/ # Page‑level components, handles business logic, passes configs to children
```

### Styling (Strict Priority)

1. Vuetify utility classes (spacing, typography, colors, flexbox)
2. Vuetify component props (`dense`, `elevation`, `outlined` …)
3. Global SCSS variables (theme overrides, defined in `assets/css/variables.css`)
4. Scoped `<style scoped>` → **only** for complex animations, brand gradients, or truly unique elements.

- Every style must support dark theme — use design tokens.
- Never add global CSS outside `variables.css` or Vuetify overrides.

### Components

- Fully configurable through typed config objects.
- **Zero business logic** — emit events and let the view/parent handle it.
- Always check if a generic `components/common` component can be reused before building something new.

### State & API

- All HTTP requests originate in `services/` (Axios instance with interceptors).
- Pinia stores: call services → cache/wrangle data → expose reactive state.
- **Components never call `axios`/`fetch` directly**; they read stores and dispatch actions.

### Routing

- Lazy‑load all view components.
- Nested routes where a view acts as a layout shell.
- Route definitions separated: `public.ts` (unauthenticated), `private.ts` (authenticated).

## 5. Feature Development Workflow

When building a new end‑to‑end feature:

1. **Backend**
   - Define models (use `BetterModelMixin`, respect multi‑tenant boundaries).
   - Create service layer if external APIs are involved.
   - Write DRF serializers & ViewSets, consuming service/orchestration.
   - Add tenant‑isolation tests and mock all external calls.
   - Document public/tenant‑schema decisions in `documentation/`.

2. **Frontend** (if new Vue UI)
   - Define config types in `config/types/` and defaults in `config/defaults/`.
   - Reuse or create generic components (`common/`) and layout components (`layout/`).
   - Build the view (business logic goes here, not in components).
   - Add routes to the appropriate route file.
   - Create service/store modules only if new API endpoints or shared state are required.
   - Verify the feature with dark theme and responsive breakpoints.

3. **Cross‑cutting**
   - Add any required Celery tasks (PDFs, emails).
   - If a legacy Django template needs updating, prefer minimal changes; new UI should go into Vue.

## 6. Anti‑Patterns (Both Backend & Frontend)

- Calling `fetch`/`axios` in a component, store, or Django view.
- Adding global CSS without using design tokens or SCSS variables.
- Embedded business logic inside UI components or templates.
- Bypassing the service layer for third‑party API calls.
- Hardcoding content — all text and behaviour must be driven by configs, backend data, or environment variables.
- Missing atomic transactions when updating multiple related records.
- Creating one‑off components when a generic, configured component would suffice.

**Reference**: For deeper architectural decisions, refer to `documentation/` (e.g., `Razorpay_Integration_Spec.md`) and the respective `README.md` files in the backend and frontend roots.
