---
title: BMA Documentation Index
type: architecture
app: core
last_updated: 2026-06-15
tags: [index, overview]
---

# Bill Management Application (BMA) Documentation

TL;DR: The Bill Management Application (BMA) is a multi-tenant SaaS platform for managing customers, automated invoicing, and payment collection. This documentation provides a comprehensive guide to its architecture, design patterns, and operational procedures.

This document covers the high-level index and roadmap for the BMA platform documentation.

## Documentation Index

### Core Architecture

- [**Architectural Overview**](./architecture/overview.md) — Vision, Pillars, and Tech Stack.
- [**Multi-Tenancy**](./architecture/multi-tenancy.md) — Schema-level isolation and implementation.
- [**Data Modeling**](./architecture/data-models.md) — Database relationships and auditing.
- [**Asynchronous Task System**](./architecture/async-system.md) — Celery, Valkey, and task registry.
- [**Frontend Architecture**](./architecture/frontend.md) — Vue 3, Pinia, and component boundaries.
- [**Authentication**](./architecture/authentication.md) — Authentication flow and Token/Session controls.

### Design Patterns

- [**Notification Design**](./patterns/notifications.md) — Multi-channel delivery and preference logic.
- [**Payment Service Architecture**](./patterns/payments.md) — Orchestrator and service layer logic.
- [**Auditing & Base Mixins**](./patterns/auditing.md) — Reusable model logic and soft deletes.

### Integrations

- [**Razorpay Integration Spec**](./integrations/razorpay.md) — Security and signature verification.

### Operations

- [**Seeder Architecture**](./operations/seeding.md) — Idempotent data provisioning for local and production setups.

## Future Roadmap

The platform is evolving to support more complex enterprise needs:

- **Advanced Analytics**: Visual revenue trends and customer growth metrics.
- **Customer Portal**: Self-service dashboard for private customers.
- **Recurring Billing**: Automated subscription management and retry logic.
- **Global Operations**: Multi-currency and localized tax calculation.
- **Extensibility**: Webhook system for real-time external system synchronization.

---

## Related Documents
- [Architectural Overview](./architecture/overview.md)
- [Multi-Tenancy](./architecture/multi-tenancy.md)
