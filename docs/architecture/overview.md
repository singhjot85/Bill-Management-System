---
title: Architectural Overview
type: architecture
app: core
last_updated: 2026-06-15
tags: [architecture, vision, tech-stack]
---

# Architectural Overview

TL;DR: BMA's architectural vision focuses on data isolation, modular decoupling, asynchronous processing, and a configurable frontend. It uses a modern tech stack centered around Django, Vue 3, and Celery.

This document covers the fundamental principles, core pillars, and the technology stack that powers the Bill Management Application.

## Architectural Vision

BMA is designed around four fundamental principles:

1.  **Isolation by Design**: Using schema-level multi-tenancy to ensure complete data segregation between organizations.
2.  **Modular Decoupling**: Business logic is abstracted into a dedicated service and orchestration layer, keeping views and models lean.
3.  **Asynchronous First**: All heavy I/O and computational tasks (PDF generation, notifications, external API syncs) are offloaded to a persistent background worker system.
4.  **Configurable Frontend**: A "dumb-component" architecture where the UI is driven by backend configurations and typed defaults rather than hardcoded logic.

## Core Pillars

### 1. Multi-Tenancy (Shared-DB, Isolated-Schema)
BMA utilizes `django-tenants` to implement a shared-database, isolated-schema architecture. This provides the best balance between resource efficiency and data security. See [Multi-Tenancy](./multi-tenancy.md) for details.

### 2. Service & Orchestration Layer
To maintain maintainability, BMA avoids the "Fat Model" or "Fat View" anti-patterns:
- **Service Layer**: Encapsulates 3rd-party integrations (e.g., Razorpay, Email Providers). Services are stateless and handle raw API communication.
- **Orchestration Layer**: Coordinates multiple services and Django models. It handles complex business workflows within atomic transactions.

### 3. Asynchronous Engine
Background processing is handled by **Celery** using **Valkey** as a persistent broker. See [Asynchronous Task System](./async-system.md) for details.

### 4. Configurable Frontend (Vue 3)
The frontend is a Vue 3 SPA that follows a strict hierarchical structure of common components, view components, service modules, and Pinia stores. See [Frontend Architecture](./frontend.md) for details.

## Tech Stack

| Layer               | Technology                                             |
| :------------------ | :----------------------------------------------------- |
| **Backend**         | Django 5.2, Django REST Framework                      |
| **Frontend**        | Vue 3 (Composition API), Vuetify 3, Vite, Pinia        |
| **Multi-Tenancy**   | `django-tenants` (PostgreSQL Schemas)                  |
| **Worker / Broker** | Celery, Valkey                                         |
| **Database**        | PostgreSQL                                             |
| **Infrastructure**  | Docker, Compose, Make                                  |

---

## Related Documents
- [Multi-Tenancy](./multi-tenancy.md)
- [Asynchronous Task System](./async-system.md)
- [Frontend Architecture](./frontend.md)
