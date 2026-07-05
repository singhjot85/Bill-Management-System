---
title: Frontend Architecture
type: architecture
app: core
last_updated: 2026-06-15
tags: [frontend, vue, vite, vuetify, pinia]
---

# Frontend Architecture

TL;DR: The frontend is a Vue 3 SPA built with Vite and Vuetify 3. It follows a decoupled architecture, communicating with the backend via a service layer and managing state with Pinia.

This document covers the technology stack, high-level architecture, state management, and key workflows of the BMA frontend.

## Tech Stack
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **UI Component Library**: Vuetify 3
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios

## High-Level Architecture

The frontend is a standalone SPA residing in `frontend/`. In development, Vite proxies `/api` requests to the Django backend.

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

We use specialized stores to manage reactive state:
- **Auth Store**: Session management, user roles, and tokens.
- **Config Store**: Global UI configurations (logos, branding) fetched from the tenant's backend.
- **Business Stores**: Feature-specific stores (e.g., `DonationStore`) to manage complex workflows.

## Key Workflows

### Donation/Payment Workflow
Complex multi-step processes are managed via **Composables** (e.g., `useDonation`), which orchestrate several API calls into a single reliable sequence.

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

## Theme & Styling
- **CSS Variables**: Global properties defined in `src/assets/variables.css` for light/dark mode.
- **Vuetify**: Configured to consume CSS variables for consistent component styling.
- **Priority**: Vuetify classes → props → SCSS variables → scoped CSS.

---

## Related Documents
- [Architectural Overview](./overview.md)
- [Payment Service Architecture](../patterns/payments.md)
