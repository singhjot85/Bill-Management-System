# Bill Management Application (BMA)

A modern, multi-tenant SaaS platform for generating, managing, and paying bills/invoices. BMA provides a seamless experience for vendors to manage their clients and for users to make payments and track their invoices.

## Core Features

- **Multi-Tenant Architecture**: Robust isolation between organizations using database schemas (via `django-tenants`).
- **Dynamic Branding**: Tenants can customize their portal with specific logos, colors, and contact information.
- **Automated Invoicing**: Generate professional PDF invoices upon payment or on-demand.
- **Integrated Payments**: Support for Razorpay and other payment gateways.
- **Role-Based Access**:
  - **Platform Admin**: Global system management and tenant provisioning.
  - **Tenant Admin**: Organization-specific management of customers and billing.
  - **Client/User**: View, download, and pay invoices.
  - **Public User**: Fast-track payment and invoice generation without account creation.

## Tech Stack

<p align="center">
  <img src="assets/django-logo-negative.png" width="150" height="80" alt="Django Logo" />
  <img src="assets/drf-logo-dark.png" width="150" height="80" alt="DRF Logo" />
  <img src="assets/vue-logo.png" width="100" height="80" alt="Vue Logo" />
  <img src="assets/celery-logo.webp" width="100" height="80" alt="celery logo" />
  <img src="assets/elephant.png" width="100" height="80" alt="postgres logo" />
  <img src="assets/docker-mark-ocean-blue.svg" width="100" height="80" alt="docker logo" />
</p>

---

| Component          | Technologies                                    |
| :----------------- | :---------------------------------------------- |
| **Backend**        | Django 5.2, DRF, django-tenants                 |
| **Frontend**       | Vue 3 (Composition API), Vite, Vuetify 3, Pinia |
| **Worker/Queue**   | Celery, Valkey                                  |
| **Database**       | PostgreSQL                                      |
| **Infrastructure** | Docker, Compose, Poetry, Pre-Commit             |

## Project Structure

The codebase is organized into dedicated directories to ensure a clean separation of concerns and optimized build processes.

- **`backend/`**: Contains the complete Django project, including apps, configuration, and management scripts.
- **`frontend/`**: Contains the Vue 3 SPA, including components, assets, and build configuration.
- **`compose/`**: Docker Compose configuration files for various environments.
- **`documentation/`**: Architectural specifications, diagrams, and developer guides.
- **Root Directory**: Houses environment variables (`.env`), CI/CD configurations, repository-wide tools (`Makefile`, `pre-commit`), and project metadata.

### Rationale: Build Isolation

This structure is designed to leverage **Docker BuildKit's** context isolation:

- During the backend build, only the `backend/` directory is provided as context.
- During the frontend build, only the `frontend/` directory is provided as context.

This eliminates accidental leakage of irrelevant code (e.g., frontend source in the backend image) and ensures that changes in one domain do not unnecessarily invalidate the build cache of the other.

## Documentation

- [Frontend Architecture](./documentation/Frontend_Architecture.md)
- [Data Models](./documentation/Models.md)
- [Local Setup & Seeders](./documentation/Local_Setup.md)
- [Payment Service Architecture](./documentation/Payment_Service_Architecture.md)

_For legacy UI documentation, see [Project Templating](./project_templating/Readme.md)._

## Local Development Setup

### 1. Build and Start Containers

```bash
make build
make up
```

### 2. Bootstrap the Database

Initialize the multi-tenant environment by seeding base tenants and users:

```bash
# Run all seeders
make setup
```

## User Credentials (Local Development)

The following pre-configured accounts are available for testing:

| Role                         | Username              | Password     | Domain                     |
| :--------------------------- | :-------------------- | :----------- | :------------------------- |
| **Platform Admin**           | `admin@localhost.com` | `qwerty@123` | `localhost:8000`           |
| **Tenant Admin (NGO)**       | `admin@localngo.com`  | `qwerty@123` | `localngo.localhost:8000`  |
| **Tenant Admin (Restraunt)** | `admin@restraunt.com` | `qwerty@123` | `restraunt.localhost:8000` |
| **Client/User (NGO)**        | `client@localngo.com` | `qwerty@123` | `localngo.localhost:8000`  |

_Note: Map these domains to `127.0.0.1` in your `/etc/hosts` file for local testing._
