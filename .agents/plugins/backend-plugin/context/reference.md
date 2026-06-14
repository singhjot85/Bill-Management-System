# Backend Plugin — Reference Context

This file points to project-specific architectural patterns, decisions, and
specifications that subagents need as reference material. Unlike `conventions.md`
(HOW to write code) and `constraints.md` (WHAT NOT to do), this file provides
the WHAT and WHY of existing design decisions so subagents build consistently
with what already exists.

`context_builder.py` injects sections selectively — based on what the feature
touches, not everything at once. The Architect's `architect_notes` in
`plugin_state.json` must declare which domains the feature touches so
`context_builder.py` knows which sections to pull.

---

## Injection Instruction for `context_builder.py`

```yaml
required: warn_and_continue
resolution: >
  Read plugin_state.json → architect_notes to determine which domains
  the feature touches. Inject only the matching domain sections below.
  If architect_notes is empty, inject ALL sections and warn the Architect
  to be more specific next time.
inject_format: >
  === REFERENCE: {domain} ===
  <extracted content>
  === END REFERENCE ===
```

---

## Domain: async_tasks

```yaml
inject_when: >
  Feature touches Celery tasks, Beat scheduling, periodic jobs,
  PDF generation, notifications, or any background processing.
inject_for_stages:
  - architecture
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
sources:
  - file: documentation/Asynchronous_Architecture.md
    sections:
      - "Infrastructure Decisions"
      - "Task File Structure"
      - "Task Discovery & Naming"
      - "Multi-Tenancy & Task Context"
      - "Failure Classification System"
      - "Periodic Tasks & Beat Fan-Out"
      - "Canvas Primitives: group vs chord"
      - "Things to remember in an Async Task"
  - file: backend/apps/tasks/Readme.md
    required: warn_and_continue
    missing_caveat: >
      backend/apps/tasks/Readme.md is missing. Refer to
      documentation/Asynchronous_Architecture.md for task implementation patterns.
```

---

## Domain: payments

```yaml
inject_when: >
  Feature touches payment processing, Razorpay integration, payment status
  transitions, webhook handling, or invoice payment flows.
inject_for_stages:
  - architecture
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
sources:
  - file: documentation/Payment_Service_Architecture.md
    sections:
      - All sections
    required: warn_and_continue
    missing_caveat: >
      documentation/Payment_Service_Architecture.md is missing.
      Do not implement payment flows without it. Flag as a prerequisite gap.
  - file: documentation/Razorpay_Integration_Spec.md
    sections:
      - All sections
    required: warn_and_continue
    missing_caveat: >
      documentation/Razorpay_Integration_Spec.md is missing.
      Do not implement Razorpay-specific logic without it. Flag as prerequisite gap.
  - file: backend/apps/payments_management/Readme.md
    required: warn_and_continue
    missing_caveat: >
      [CONTEXT WARNING] backend/apps/payments_management/Readme.md is missing.
      Conventions for this app are unknown. Do not make assumptions about its
      internal structure. Stick strictly to project-wide conventions from
      backend/Readme.md until this file exists.
```

---

## Domain: tenants

```yaml
inject_when: >
  Feature touches tenant provisioning, OrganizationTenant model, branding,
  schema creation, or any public-schema logic.
inject_for_stages:
  - architecture
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
sources:
  - file: documentation/Models.md
    sections:
      - "Tenants (Public Schema)"
    required: hard_stop
    reason: >
      Tenant model definitions are non-negotiable reference. Without them
      the agent cannot reason about schema isolation correctly.
  - file: backend/apps/tenants/Readme.md
    required: warn_and_continue
    missing_caveat: >
      [CONTEXT WARNING] backend/apps/tenants/Readme.md is missing.
      Conventions for this app are unknown. Do not make assumptions about its
      internal structure. Stick strictly to project-wide conventions from
      backend/Readme.md until this file exists.
```

---

## Domain: customers

```yaml
inject_when: >
  Feature touches Customer model, CustomerAddress, customer types,
  verification flows, or any customer-facing API.
inject_for_stages:
  - architecture
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
sources:
  - file: documentation/Models.md
    sections:
      - "Customer Management (Tenant Schema)"
    required: hard_stop
    reason: >
      Customer model definitions are the canonical reference for this domain.
  - file: backend/apps/customer_management/Readme.md
    required: warn_and_continue
    missing_caveat: >
      [CONTEXT WARNING] backend/apps/customer_management/Readme.md is missing.
      Conventions for this app are unknown. Do not make assumptions about its
      internal structure. Stick strictly to project-wide conventions from
      backend/Readme.md until this file exists.
```

---

## Domain: notifications

```yaml
inject_when: >
  Feature touches email, SMS, admin alerts, or any outbound communication.
inject_for_stages:
  - architecture
  - happy_path
  - full_implementation
inject_for_agents:
  - architect
  - coder
sources:
  - file: backend/apps/notifications/Readme.md
    sections:
      - All sections
    required: warn_and_continue
    missing_caveat: >
      backend/apps/notifications/Readme.md is missing.
      Do not implement notification logic without reviewing existing patterns.
      Flag this gap in architect_notes.
```

---

## Domain: setup_and_config

```yaml
inject_when: >
  Feature introduces new external service configuration (e.g. a new payment
  gateway, a new API key), modifies the Configurations model, or adds new
  environment-dependent settings.
inject_for_stages:
  - architecture
  - dependency_setup
inject_for_agents:
  - architect
  - coder
sources:
  - file: documentation/Models.md
    sections:
      - "Setup (Tenant Schema)"
    required: hard_stop
    reason: >
      The Configurations model pattern must be followed for all new
      service configurations. Hardcoding config is a constraint violation.
  - file: backend/apps/setup/Readme.md
    required: warn_and_continue
    missing_caveat: >
      [CONTEXT WARNING] backend/apps/setup/Readme.md is missing.
      Conventions for this app are unknown. Refer to documentation/Models.md
      § "Setup (Tenant Schema)" as the primary reference.
```

---

## Domain: seeders

```yaml
inject_when: >
  Feature introduces new models, new tenant-level data, or new configuration
  entries that need to be present in a fresh development environment.
inject_for_stages:
  - full_implementation
  - final_documentation
inject_for_agents:
  - coder
sources:
  - file: documentation/Seeder_Architecture.md
    sections:
      - All sections
    required: warn_and_continue
    missing_caveat: >
      documentation/Seeder_Architecture.md is missing. If this feature requires
      seeded data, flag it in architect_notes and ask the user how to proceed.
```

---

## Domain: architecture_index

```yaml
inject_when: >
  Architect subagent is running at the architecture stage for any feature.
  Always injected for architect agent regardless of domain.
inject_for_stages:
  - architecture
inject_for_agents:
  - architect
sources:
  - file: documentation/Readme.md
    sections:
      - All sections
    required: hard_stop
    reason: >
      The documentation index is the Architect's primary orientation point.
      Without it, the Architect cannot know what has already been designed
      and risks duplicating or contradicting existing decisions.
```

---

## Maintenance Note

When a new architecture document is added to `documentation/`, add a corresponding
domain entry here. When a new app is added to `backend/apps/`, add it to both
`conventions.md → known_apps` and create a domain entry here if it has a distinct
concern. This file and `conventions.md` are the two files that need updating when
the project grows — they are the single point of truth for what context the agents
receive.
