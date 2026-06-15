# Tenants Management Module

This module serves as the core foundation for the multi-tenant architecture of the Bill Management System (BMA). It leverages `django-tenants` to provide schema-level isolation for different organizations while maintaining a shared public schema for global data.

## 1. Architectural Flow

The multi-tenancy flow is built on the **Schema-per-Tenant** strategy:

1.  **Request Routing**: Incoming requests are routed based on the domain (or subdomain). The `TenantMainMiddleware` identifies the tenant from the `OrganizationDomain` and sets the PostgreSQL search path to the corresponding schema.
2.  **Shared vs. Isolated Data**:
    *   **Public Schema**: Contains global models such as `OrganizationTenant`, `OrganizationDomain`, `User`, and `OrganizationBranding`. These are accessible across all tenants.
    *   **Tenant Schemas**: Contains isolated data for customer management, invoices, notifications, etc.
3.  **Branding Lifecycle**:
    *   The frontend queries the `BrandingViewSet` using the `tenant` schema name.
    *   `OrganizationBranding` provides tenant-specific UI configuration (logos, titles, footers).
    *   The `get_current_branding` helper on the model allows backend services to retrieve the branding of the currently active schema.
4.  **Authentication**:
    *   Users are stored in the public schema but can be authenticated from any tenant domain.
    *   `AuthViewSet` manages session-based login/logout.

## 2. Design Patterns

*   **Schema Isolation (Database Level)**: Ensures strict data separation between different organizations at the database layer.
*   **Singleton Branding**: Each `OrganizationTenant` is linked via a `OneToOneField` to `OrganizationBranding`, ensuring a unique UI identity for every tenant.
*   **Mixin-Based Models**:
    *   `SafeModelMixin`: Implements soft-delete (`is_removed`) and timestamps (`created`, `modified`).
    *   `VersionedBetterModelMixin`: Adds UUID primary keys and semantic versioning (`major`, `minor`, `patch`) to branding records.
*   **Specialized Admin**: Uses a `public_admin_site` to manage shared models, preventing them from appearing in tenant-specific admin interfaces.

## 3. Developer Guide

### Creating a New Tenant
To onboard a new organization:
1.  Create an `OrganizationTenant` record with a unique `schema_name`.
2.  Create an `OrganizationDomain` record pointing to that tenant.
3.  (Optional) Initialize `OrganizationBranding` to customize the tenant's UI.

### Extending Branding
If you need to add new configuration fields (e.g., primary color, social links):
1.  Add the field to `OrganizationBranding` in `models.py`.
2.  Update `BrandingSerializer` in `serializers.py` to expose it.
3.  Update the `OrgBrandingAdmin` in `admin.py` to include it in the fieldsets.

### Authentication
Use the `AuthViewSet` endpoints:
*   `POST /api/auth/login/`: Standard login.
*   `POST /api/auth/logout/`: Standard logout (requires auth).
*   `GET /api/auth/me/`: Get current user details.

## 4. Directory Structure

| File | Purpose |
| :--- | :--- |
| `models.py` | Defines `OrganizationTenant`, `OrganizationDomain`, and `OrganizationBranding`. |
| `views.py` | ViewSets for Authentication and Branding retrieval. |
| `serializers.py` | Serializers for Users, Login, and Branding models. |
| `admin.py` | Registration of models on the `public_admin_site` with custom fieldsets. |
| `constants.py` | Choices and static mapping (e.g., `CountryChoices`). |
| `apps.py` | Django app configuration. |

## 5. Operational Guardrails

*   **Tenant Schema Integrity**: Never perform cross-schema queries manually. Rely on `django-tenants` logic and the service layer.
*   **Public Models**: Models in this app (`OrganizationTenant`, etc.) are critical system components. Do not move them to `TENANT_APPS` as they must reside in the public schema.
*   **Admin Registration**: Always use `public_admin_site.register()` for models in this app to ensure they are managed globally.
*   **Soft Deletion**: Use `available_objects` manager or `is_removed=False` filter when querying tenants to respect soft-deletion.
*   **Schema Names**: Ensure `schema_name` follows valid PostgreSQL identifier rules (lowercase, no special characters except underscores).
