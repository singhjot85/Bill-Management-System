# Frontend Architecture: Vue 3 + Vite SPA

This document outlines the architecture and implementation details of the decoupled frontend for the Bill Management System.

## Tech Stack
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **UI Component Library**: Vuetify 3
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Styling**: CSS Variables (Variables.css) + SCSS

## High-Level Architecture

The frontend is a standalone Single Page Application (SPA) that resides in the `frontend/` directory. It communicates with the Django REST API through a proxy configured in Vite, avoiding CORS issues during development.

```mermaid
graph TD
    User((User))
    ViteServer[Vite Dev Server :5173]
    DjangoAPI[Django API :8000]
    Postgres[(PostgreSQL)]

    User -->|Access| ViteServer
    ViteServer -->|Static Assets| User
    ViteServer -->|Proxy /api| DjangoAPI
    DjangoAPI -->|Data| Postgres
```

## State Management (Pinia)

The application uses three primary stores:
1.  **Auth Store**: Manages user session, roles (e.g., `client_admin`), and tokens.
2.  **Config Store**: Holds global configurations like App Name, Logo URL, and feature flags.
3.  **Donation Store**: Manages the multi-step state of the donation workflow.

## Key Workflows

### Donation Workflow
The donation process is managed by the `useDonation` composable, ensuring a reliable and retryable sequence.

```mermaid
sequenceDiagram
    participant U as User
    participant V as Vue Component
    participant C as useDonation Composable
    participant A as Django API

    U->>V: Fill Form & Submit
    V->>C: processDonation()
    C->>A: POST /validate_email/
    C->>A: POST /validate_phone/
    alt Validation Successful
        C->>A: POST /make_payment/
        A-->>C: payment_id
        C->>A: POST /submit_form/
        A-->>C: unique_code
        C->>V: Redirect to Success
    else Validation Failed
        C->>V: Display Field Errors
    end
```

## Integration & Deployment
- **Docker**: The frontend is containerized using a multi-stage Dockerfile (`compose/local/vue/Dockerfile`).
- **Proxy**: In development, Vite proxies `/api` to the `django` service defined in Docker Compose.
- **Environment Variables**:
    - `VITE_API_BASE_URL`: Base endpoint for API calls.
    - `VITE_APP_NAME`: Configurable branding.
    - `VITE_BUILD_TAG`: Displayed in the footer for version tracking.

## Theme & Styling
Styles are managed via `src/assets/variables.css`, which defines CSS custom properties for light and dark modes. Vuetify is configured to consume these variables, ensuring a unified look across all components.
