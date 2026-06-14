# Notification App — Implementation Guide

This app manages the lifecycle of all outbound communications (Email, SMS, Webhooks) within the BMA platform. It is designed to be highly decoupled, multi-tenant aware, and asynchronous.

For a high-level overview of the design philosophy, see [Notification Architecture](../../documentation/Notfications.md).

## Implementation Architecture

The notification flow is split into four distinct phases to ensure reliability and maintainability:

1.  **Trigger**: Capture the intent and data (Synchronous).
2.  **Resolve**: Intersect tenant permissions with user preferences (Synchronous).
3.  **Dispatch**: Log the intent and hand off to the worker (Synchronous).
4.  **Execute**: Render templates and perform network I/O (Asynchronous).

## Design Patterns in Use

- **Observer / Event-Driven**: Triggers are decoupled from implementation. Emitting an event (`NotificationEvent`) initiates the flow.
- **Strategy Pattern**: Delivery logic is encapsulated in strategies (e.g., `EmailStrategy`, `SMSStrategy`), allowing different providers for different channels.
- **Command Pattern**: `ChannelInstruction` acts as a command object that stores all state required for the async task to execute correctly.
- **Factory Pattern**: `ResolverFactory` dynamically selects the appropriate resolution logic based on the event and party types.
- **Facade Pattern**: `NotificationService` (and the `trigger_notifications` helper) provides a simplified entry point to the complex internal workflow.

## How to Add a New Notification

### 1. Register the Event

Add the new event to `EventTypeChoices` and define its allowed channels in `EventPreferences` within `backend/apps/notifications/constants.py`.

```python
class EventTypeChoices(TextChoices):
    NEW_INVOICE = "new_invoice", "New Invoice Generated"

class EventPreferences(Enum):
    NEW_INVOICE = "new_invoice", [ChannelTypeChoices.EMAIL.value, ChannelTypeChoices.SMS.value]
```

### 2. Create Templates

Add the corresponding templates in the `NotificationTemplate` table (usually via seeders or admin). Templates support Django/Jinja-like variable substitution.

### 3. Trigger the Notification

Call the `trigger_notifications` utility from anywhere in the backend (Views, Services, or Tasks).

```python
from apps.notifications.workflow.trigger import trigger_notifications

trigger_notifications(
    event_type=EventTypeChoices.NEW_INVOICE,
    assosciated_parties=[customer.uuid],
    data={"invoice_number": "INV-001", "amount": 500}
)
```

## Directory Structure

- `workflow/trigger.py`: Entry point for initiating a notification flow.
- `workflow/resolvers/`: Brains of the system; handles preference intersections and template selection.
- `workflow/dispatcher.py`: Handles `NotificationLog` creation and Celery task enqueuing.
- `workflow/stratergies/`: Implementation of channel-specific delivery logic.
- `models.py`: Definitions for `NotificationTemplate`, `NotificationLog`, and `NotificationPreferences`.

## Critical Rules

1.  **No Network I/O in Resolver**: The resolver must be fast and only perform database reads.
2.  **Tenant Isolation**: Always ensure `assosciated_parties` belong to the active tenant schema.
3.  **Atomic Transactions**: Triggers should ideally happen after a database commit to ensure the worker can find the related data.
