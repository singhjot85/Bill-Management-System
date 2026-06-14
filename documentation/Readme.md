# Bill Management Application (BMA) — Architecture & Design

The Bill Management Application (BMA) is a high-performance, multi-tenant SaaS platform designed for organizations to manage customers, automate invoice generation, and streamline payment collection.

Built with scalability and strict data isolation at its core, BMA serves as a robust blueprint for modern enterprise applications.

## Architectural Vision

BMA is designed around four fundamental principles:

1.  **Isolation by Design**: Using schema-level multi-tenancy to ensure complete data segregation between organizations.
2.  **Modular Decoupling**: Business logic is abstracted into a dedicated service and orchestration layer, keeping views and models lean.
3.  **Asynchronous First**: All heavy I/O and computational tasks (PDF generation, notifications, external API syncs) are offloaded to a persistent background worker system.
4.  **Configurable Frontend**: A "dumb-component" architecture where the UI is driven by backend configurations and typed defaults rather than hardcoded logic.

## Core Pillars

### 1. Multi-Tenancy (Shared-DB, Isolated-Schema)

BMA utilizes `django-tenants` to implement a shared-database, isolated-schema architecture. This provides the best balance between resource efficiency and data security.

- **Public Schema**: Houses platform-wide data, including tenant metadata (`OrganizationTenant`), global user accounts, and shared configurations.
- **Tenant Schemas**: Every organization receives a dedicated database schema. All customer data, invoices, and payments are stored here, ensuring no cross-tenant data leakage is possible at the database level.

### 2. Service & Orchestration Layer

To maintain maintainability, BMA avoids the "Fat Model" or "Fat View" anti-patterns:

- **Service Layer**: Encapsulates 3rd-party integrations (e.g., Razorpay, Email Providers). Services are stateless and handle raw API communication.
- **Orchestration Layer**: Coordinates multiple services and Django models. It handles complex business workflows (like "Verify Payment and Generate Invoice") within atomic transactions.
- **Managers**: Custom Django Managers handle domain-specific query logic, keeping models focused on data structure.

### 3. Asynchronous Engine

Background processing is handled by **Celery** using **Valkey** as a persistent broker.

- **Broker Isolation**: We use two separate Valkey instances—one for transient caching and one for persistent task brokering.
- **Task Registry**: Tasks are explicitly named and registered, decoupling their identity from the codebase structure to allow for safe refactoring.
- **Auditability**: Task results are stored in PostgreSQL via `django-celery-results`, providing a queryable audit trail for critical failures.

### 4. Configurable Frontend (Vue 3)

The frontend is a Vue 3 Single Page Application (SPA) that follows a strict hierarchical structure:

- **Common Components**: Reusable, layout-agnostic UI pieces (buttons, cards).
- **View Components**: Handle business logic and pass configurations down to layouts.
- **Service Modules**: The only place where HTTP calls originate (via Axios).
- **Pinia Stores**: Manage reactive state and orchestrate service calls.

## Tech Stack

| Layer               | Technology                                             |
| :------------------ | :----------------------------------------------------- |
| **Backend**         | Django 5.2, Django REST Framework                      |
| **Frontend**        | Vue 3 (Composition API), Vuetify 3, Vite, Pinia        |
| **Multi-Tenancy**   | `django-tenants` (PostgreSQL Schemas)                  |
| **Worker / Broker** | Celery, Valkey                                         |
| **Database**        | PostgreSQL                                             |
| **Infrastructure**  | Docker, Compose, Make                                  |
| **Tooling**         | Poetry (Python), Pre-commit (Black/Isort/Lint), Pytest |

## Documentation Roadmap

Dive deeper into specific architectural components:

### Infrastructure & Core

- [**Data Modeling & Architecture**](./Models.md) — Database relationships and mixins.
- [**Multi-Tenancy Deep Dive**](./Readme.md#multi-tenancy) — Schema strategy and isolation rules.
- [**Seeder Architecture**](./Seeder_Architecture.md) — Local development and demo data setup.

### Backend Logic

- [**Asynchronous Architecture**](./Asynchronus_Architecture.md) — Celery workers, task registry, and Valkey setup.
- [**Notification System**](./Notfications.md) — Workflow strategies for email and SMS.
- [**Payment Service Architecture**](./Payment_Service_Architecture.md) — Orchestrating payment verification.
- [**Razorpay Integration Spec**](./Razorpay_Integration_Spec.md) — Secure signature verification and order flows.

### Frontend

- [**Frontend Architecture**](./Frontend_Architecture.md) — Component boundaries, styling priorities, and state management.

## Future Roadmap

The platform is evolving to support more complex enterprise needs:

- **Advanced Analytics**: Visual revenue trends and customer growth metrics.
- **Customer Portal**: Self-service dashboard for private customers.
- **Recurring Billing**: Automated subscription management and retry logic.
- **Global Operations**: Multi-currency and localized tax calculation.
- **Extensibility**: Webhook system for real-time external system synchronization.

> **Note**: For day-to-day coding conventions and anti-patterns, always refer to the root [**AGENTS.md**](../AGENTS.md).
