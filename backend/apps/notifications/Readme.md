---
title: Notifications
type: implementation
app: notifications
last_updated: 2026-06-15
tags: [django, notifications, celery, email, sms]
---

# Notifications

## Purpose
This app manages the lifecycle of all outbound communications (Email, SMS, Webhooks) within the BMA platform.

It is designed to be highly decoupled, multi-tenant aware, and asynchronous, ensuring that communication failures do not impact the core business workflows.

## Quick Start
Ensure the Celery worker is running to process notification tasks:
```bash
# From the project root
make worker-start
```

## Key Concepts
- **Four-Phase Flow**:
  1. **Trigger**: Capture intent synchronously.
  2. **Resolve**: Intersect tenant permissions and user preferences.
  3. **Dispatch**: Log intent and hand off to Celery.
  4. **Execute**: Asynchronous rendering and delivery.
- **Strategy Pattern**: Delivery logic is encapsulated in channel-specific strategies (Email, SMS, etc.).
- **Template Management**: Supports dynamic templates with Jinja2-style variable substitution.

## API Reference
Notifications are triggered via the `trigger_notifications` utility.

| Utility Function | Parameters | Description |
| :--- | :--- | :--- |
| `trigger_notifications` | `event_type`, `assosciated_parties`, `data` | Main entry point for any notification event |

## Configuration
- `NOTIFICATION_PROVIDERS`: Configuration for external gateways (SES, Twilio).
- `CELERY_BROKER_URL`: Connection string for Valkey/Redis.

## Testing
Test the notification workflow and async tasks:
```bash
pytest backend/tests/tasks/test_base.py
```

## Related Documentation
- [Notification Architecture](../../../docs/architecture/async-system.md)
- [Notifications Pattern](../../../docs/patterns/notifications.md)
- [System Overview](../../../docs/README.md)
