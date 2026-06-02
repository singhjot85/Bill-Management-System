# Bill Management Application (BMA)

The Bill Management Application is a robust, multi-tenant SaaS platform designed for organizations to manage customers, generate invoices, and collect payments efficiently. Built with scalability and isolation in mind, it leverages a shared-database, isolated-schema architecture.

---

## System Architecture

### Multi-Tenancy
The system uses `django-tenants` to provide strict data isolation:
- **Public Schema**: Manages global data like `OrganizationTenant` (Tenants) and `OrganizationDomain`.
- **Tenant Schemas**: Each organization has its own isolated schema containing `Customers`, `Invoices`, `Payments`, and `Branding` data.

### Service Layer & Orchestration
To maintain clean separation of concerns:
- **Models**: Simple data structures with minimal logic.
- **Services**: Encapsulate 3rd-party integrations (e.g., `RazorpayService`).
- **Orchestrators**: Coordinate between multiple services and models (e.g., `PaymentOrchestrator` handles the atomic flow of verifying a payment and updating an invoice).

### Async Task Processing
Heavy operations like PDF generation and email notifications are offloaded to **Celery** using **Valkey** as the message broker.

---

## Database Structure (Models)

### 1. Tenant & Branding (`apps.tenants`)
- **OrganizationTenant**: The core tenant model.
- **OrganizationDomain**: Domain mapping for tenants.
- **OrganizationBranding**: Stores tenant-specific UI configurations (logos, titles, footers, and contact info).

### 2. Customer Management (`apps.customer_management`)
- **Customer**: Stores user details (Public, Private, or Internal). Supports external references and metadata via JSON.
- **CustomerAddress**: Handles multiple addresses per customer, marking one as primary for billing.

### 3. Invoicing & Payments (`apps.payments_management`)
- **Invoice**: The central billing entity. Tracks dates, status (`CREATED`, `PAID`, `INVALID`), and generated documents.
- **Templates**: Versioned HTML/Plain-text templates for dynamic invoice generation.
- **Payment**: Tracks financial transactions, gateway responses, and verification status. Linked to both an `Invoice` and a `Customer`.

### 4. System Configuration (`apps.setup`)
- **Configurations**: A versioned key-value store for tenant-level settings (e.g., API keys, feature flags).

---

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework, django-tenants.
- **Frontend**: Vue 3 (Composition API), Vuetify 3, Vite, Pinia.
- **Storage**: PostgreSQL (with Schema support), Valkey (Cache/Broker).
- **Tooling**: Docker & Compose, Poetry, Pytest, Pre-commit (Black/Isort).

---

## Future Scope

The following features are planned for future releases to enhance the platform's capabilities:

1. **Advanced Analytics Dashboard**:
   - Visual insights for Tenant Admins regarding revenue trends, customer growth, and payment success rates.
2. **Customer Self-Service Portal**:
   - A dedicated dashboard for `Private` customers to view payment history, download past invoices, and manage saved addresses.
3. **Expanded Payment Gateways**:
   - Native support for PayPal, Stripe, and localized gateways for different regions.
4. **Subscription & Recurring Billing**:
   - Automated invoice generation for subscription-based services with automated retry logic for failed payments.
5. **Webhook Integration**:
   - Allow tenants to receive real-time updates in their own systems when payments are verified or invoices are created.
6. **AI-Powered Insights**:
   - Predictive analysis for payment defaults and automated reminders based on customer behavior.
7. **Multi-Currency & Multi-Language Support**:
   - Full localization support for global operations, including dynamic tax calculation based on region.

---

## Further Documentation
- [Models & Database Layout](./Models.md)
- [Frontend Architecture](./Frontend_Architecture.md)
- [Payment Service Architecture](./Payment_Service_Architecture.md)
- [Razorpay Integration Spec](./Razorpay_Integration_Spec.md)
