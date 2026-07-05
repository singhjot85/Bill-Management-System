---
title: Services & Orchestration
type: implementation
app: services
last_updated: 2026-06-15
tags: [django, services, orchestration, deprecated]
---

# Services & Orchestration [DEPRECATED]

> [!WARNING]
> This module is **DEPRECATED**. All logic within this directory is being migrated to more appropriate app-specific locations to improve modularity and reduce cross-app coupling.

## Purpose
Historically, this directory housed the shared service and orchestration layers for the BMA backend, specifically for 3rd-party API integrations like Razorpay.

## Quick Start
> [!IMPORTANT]
> This module is deprecated. No setup is required for new features. Migration is underway.

## Migration Path
New code should not be added here. Existing logic is moving as follows:

- **`base.py` (BaseHTTPService)**: Moving to `backend/utils/` as a shared utility for HTTP-based integrations.
- **`razorpay_service.py`**: Moving to `backend/apps/payments_management/services/`.
- **`payment_orchestrator.py`**: Moving to `backend/apps/payments_management/orchestrators/`.

## Key Concepts
- **Base HTTP Layer**: A low-level wrapper around the `requests` library.
- **Specific Service Layer**: Provider-specific logic (e.g., Razorpay).
- **Orchestration Layer**: Coordinates between services and Django models.

## API Reference (Legacy)
| Class | Role |
| :--- | :--- |
| `BaseHTTPService` | Low-level request handling |
| `RazorpayService` | Razorpay-specific API calls |
| `PaymentOrchestrator` | Database-to-Gateway coordination |

## Configuration
Depends on gateway-specific settings (e.g., `RAZORPAY_KEY_ID`).

## Testing
Legacy tests may still reference this directory.
```bash
pytest backend/tests/payment_management/
```

## Related Documentation
- [Payments Pattern](../../../docs/patterns/payments.md)
- [Razorpay Integration Spec](../../../docs/integrations/razorpay.md)
