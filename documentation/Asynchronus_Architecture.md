# BMA — Async Task System: Architecture Summary

Asynchronous tasks, one of the key component of backend applications. Generally, we offload heavy I/O bound or high computation jobs on them. They can be categorized in two major categories:

- **_Async Tasks:_** Similar to a normal backend process, just offloaded to seperate instance of application. Advantage is that we do not block main execution thread.
- **_Periodic Jobs:_** Tasks than run after a period of time, also in a sepreate instance of application.

> Note: Never horizontally scale a periodic job performing application, otherwise
> you'll have multiple runs of same periodic task. Ex: you'll generate two bills for one request.

_A record of all design decisions, CS concepts, and finalised approaches from the brainstorming session._

## 1. Infrastructure Decisions

### Message Broker

**Decision: Two separate Valkey instances**

- `valkey-cache` — volatile, for Django caching
- `valkey-broker` — persistent (`appendonly yes`), for Celery

**Why not RabbitMQ:** RabbitMQ is a better purpose-built broker, but Valkey is already in the stack. Separating cache and broker into two containers gives logical isolation without the operational overhead of a new technology. Revisit if task volume grows significantly.

**Why not a single Valkey instance:** Cache and broker are separate concerns. A flood of Celery tasks competing with cache reads is a resource contention problem that is trivially avoided by separation.

### Result Backend

**Decision: `django-celery-results`**

Stores task results in PostgreSQL. Rejected Valkey as result backend because:

- Valkey results expire after TTL — no long-term auditability
- Not queryable — can't ask "show me all failed tasks from yesterday"
- PostgreSQL results are persistent, queryable via ORM, and visible in Django Admin

**Optimisation:** Not every task stores results. Use `ignore_result=True` for fire-and-forget tasks where failure visibility is not needed.

```python
@app.task(ignore_result=True)
def send_reminder_email(...):
    ...  # no audit trail needed

@app.task  # result stored
def generate_invoice_pdf(...):
    ...  # failure visibility matters
```

### Beat Scheduler

**Decision: `django-celery-beat` with `DatabaseScheduler`**

Schedule lives in PostgreSQL, manageable via Django Admin at runtime — no redeployment needed to add/modify/disable jobs. Initial static schedule is defined in `config/celery_config.py` and imported into DB on first run.

## 2. Task File Structure

**Decision: Dedicated `project_apps/tasks/` module**

Rejected per-app `tasks.py` files because periodic and notification tasks are cross-cutting concerns that touch multiple apps. A dedicated module prevents implicit coupling between apps through the task layer.

```
project_apps/
|- tasks/
|   |- __init__.py
|   |- base.py              # TenantAwareTask, TenantFanOut, failure handling
|   |- invoice_tasks.py     # PDF generation, invoice status updates
|   |- notification_tasks.py # Emails, SMS
|   |- periodic_tasks.py    # Coordinator tasks (Beat-scheduled)
|   |- registry.py          # Task name constants
```

## 3. Task Discovery & Naming

### Discovery

**Decision: Explicit `autodiscover_tasks` list**

`autodiscover_tasks()` with no arguments won't find `project_apps/tasks/` because it is not in `INSTALLED_APPS`. Explicit registration is consistent with the project's convention of explicit URL routing in `config/routers.py`.

```python
# config/celery.py
app.autodiscover_tasks([
    'project_apps.tasks.invoice_tasks',
    'project_apps.tasks.notification_tasks',
    'project_apps.tasks.periodic_tasks',
])
```

### Naming

**Decision: Explicit task names via `registry.py`**

Default names derived from module paths break if files are renamed or moved — Beat schedules, DLQ entries, and in-flight broker messages all reference the name as a string. Explicit names decouple the task's identity from its file location.

```python
# project_apps/tasks/registry.py
class TaskNames:
    GENERATE_INVOICE_PDF             = 'bma.invoice.generate_pdf'
    SEND_PAYMENT_NOTIFICATION        = 'bma.notification.payment'
    COORDINATE_MARK_DEFAULTED        = 'bma.periodic.coordinate_mark_defaulted'
    COORDINATE_PAYMENT_REMINDERS     = 'bma.periodic.coordinate_payment_reminders'
    COORDINATE_STALE_PAYMENT_CLEANUP = 'bma.periodic.coordinate_cleanup'
```

The `bma.*` prefix namespace also powers zero-maintenance queue routing:

```python
CELERY_TASK_ROUTES = {
    'bma.invoice.*':      {'queue': 'heavy'},
    'bma.notification.*': {'queue': 'fast'},
    'bma.periodic.*':     {'queue': 'scheduled'},
}
```

New tasks added under the right prefix are automatically routed correctly.

## 4. Multi-Tenancy & Task Context

### Why `tenant-schemas-celery` was rejected

The library is low-activity (540 weekly downloads, no releases in 12+ months, companion `django-tenants-celery-beat` classified as inactive). More importantly, the library's core logic is ~30 lines — owning it explicitly is safer and more educational.

### `TenantAwareTask` Base Class

Solves the core problem: Celery workers have no active HTTP request, so `connection.schema_name` is meaningless in a worker process without explicit injection.

**CS Concept: Template Method Pattern** — base class defines the execution skeleton (schema injection → execution → failure routing), subclasses declare the specifics (failure mode, task logic).

```python
# project_apps/tasks/base.py

class TenantAwareTask(Task):
    abstract = True

    def apply_async(self, args=None, kwargs=None, **options):
        kwargs = kwargs or {}
        # Only auto-inject if schema not explicitly provided (fan-out path)
        if '_schema_name' not in kwargs:
            kwargs['_schema_name'] = connection.schema_name
        return super().apply_async(args, kwargs, **options)

    def __call__(self, *args, **kwargs):
        # Explicit schema_name (fan-out) takes priority over auto-injected
        schema_name = (
            kwargs.pop('schema_name', None) or
            kwargs.pop('_schema_name', 'public')
        )
        with schema_context(schema_name):
            return super().__call__(*args, **kwargs)
```

**Key rules:**

- Always pass IDs and schema names to tasks — never model instances
- Idempotency guards inside every task — Celery will retry, side effects must be safe to repeat

## 5. Failure Classification System

**Decision: Three-tier failure classification via Strategy Pattern**

Not all failures are equal. The system classifies failures at task declaration time, not handling time.

### Failure Tiers

| Tier     | Behaviour                                                   | Use Case                                           |
| -------- | ----------------------------------------------------------- | -------------------------------------------------- |
| `SILENT` | Log + mark result. No notification.                         | Weekly cleanup jobs — missing once is acceptable   |
| `ALERT`  | Log + notify admin (Sentry/email).                          | Invoice PDF failure — human needs to know          |
| `DLQ`    | Move to Dead Letter Queue + Alert. Manual replay supported. | Emails/SMS — need to be replayed, not just alerted |

### Failure Type Classification (inside tasks)

```python
except Invoice.DoesNotExist:
    return  # Permanent failure — don't retry, return silently

except Exception as exc:
    raise self.retry(exc=exc, countdown=2 ** self.request.retries)  # Transient — exponential backoff
```

### `TenantAwareTask` with Failure Routing

```python
class FailureMode:
    SILENT = "silent"
    ALERT  = "alert"
    DLQ    = "dlq"

class TenantAwareTask(Task):
    abstract = True
    failure_mode = FailureMode.SILENT  # default

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.failure_mode == FailureMode.SILENT:
            self._handle_silent(exc, task_id)
        elif self.failure_mode == FailureMode.ALERT:
            self._handle_alert(exc, task_id, einfo)
        elif self.failure_mode == FailureMode.DLQ:
            self._handle_dlq(exc, task_id, args, kwargs, einfo)
```

### Task Declaration

```python
@app.task(name=TaskNames.GENERATE_INVOICE_PDF, bind=True,
          base=TenantAwareTask, failure_mode=FailureMode.DLQ)
def generate_invoice_pdf(self, invoice_id, **kwargs):
    ...

@app.task(name=TaskNames.SEND_PAYMENT_NOTIFICATION, bind=True,
          base=TenantAwareTask, failure_mode=FailureMode.ALERT)
def send_payment_notification(self, payment_id, **kwargs):
    ...
```

### Dead Letter Queue Model

Lives in public schema (infrastructure-level concern, not tenant data).

```python
class DeadLetterEntry(TimeStampedModel):
    task_name   = models.CharField(max_length=255)
    task_id     = models.UUIDField()
    args        = models.JSONField(default=list)
    kwargs      = models.JSONField(default=dict)  # contains _schema_name
    exception   = models.TextField()
    traceback   = models.TextField()
    status      = models.CharField(
        choices=["PENDING_REVIEW", "REPLAYED", "DISMISSED"],
        default="PENDING_REVIEW"
    )
    replayed_at = models.DateTimeField(null=True)
    replayed_by = models.ForeignKey(User, null=True)
```

**Replay endpoint (conceptual):**

```python
def replay(self, request, pk):
    entry = DeadLetterEntry.objects.get(pk=pk, status="PENDING_REVIEW")
    task  = celery_app.tasks[entry.task_name]
    task.apply_async(args=entry.args, kwargs=entry.kwargs)
    # kwargs already contains _schema_name — tenant context is preserved
    entry.status      = "REPLAYED"
    entry.replayed_at = now()
    entry.replayed_by = request.user
    entry.save()
```

## 6. Periodic Tasks & Beat Fan-Out

### The Beat + Multi-Tenancy Problem

Beat fires tasks as a standalone process with no active tenant. `connection.schema_name` is `'public'` — the auto-injection in `TenantAwareTask.apply_async` would silently pass the wrong schema to every scheduled task. This is a **silent correctness bug**, not a crash.

**Solution: Two-level coordinator pattern**

Beat fires only coordinator tasks (public schema). Coordinators discover tenants and fan out per-tenant subtasks.

```
Beat → coordinator task (public schema)
            └── group/chord of per-tenant tasks
                    └── TenantAwareTask with explicit schema_name
```

### `TenantPeriodicTaskConfig` Model

**Decision: Composition over inheritance**

Inheriting from `django-celery-beat`'s `PeriodicTask` creates Django multi-table inheritance — Beat's own queries don't join the child table, making the extension invisible to the scheduler. Composition via `OneToOneField` extends the model cleanly without touching Beat's internals.

**Decision: ManyToManyField over JSONField for tenant list**

JSONField has no referential integrity — stale schema names remain silently after a tenant is deleted. ManyToManyField gives cascade deletion, queryability (`org.periodic_task_configs.all()`), and a proper Admin multi-select widget.

```python
class TenantPeriodicTaskConfig(models.Model):
    periodic_task = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        related_name='tenant_config'
    )
    tenants = models.ManyToManyField(
        OrganizationTenant,
        blank=True,
        related_name='periodic_task_configs'
    )
    run_for_all_tenants    = models.BooleanField(default=True)
    auto_enroll_new_tenants = models.BooleanField(default=False)
```

`run_for_all_tenants=True` dynamically queries all active tenants (no data maintenance). `run_for_all_tenants=False` uses the explicit `tenants` M2M list — enabling per-tenant feature toggling.

New tenant auto-enrolment via signal:

```python
@receiver(post_save, sender=OrganizationTenant)
def enroll_default_periodic_tasks(sender, instance, created, **kwargs):
    if not created:
        return
    for config in TenantPeriodicTaskConfig.objects.filter(auto_enroll_new_tenants=True):
        config.tenants.add(instance)
```

### `TenantPeriodicTaskWrapper`

Resolves the tenant list at runtime:

```python
class TenantPeriodicTaskWrapper:
    @staticmethod
    def get_target_schemas(periodic_task_name: str) -> list[str]:
        config = TenantPeriodicTaskConfig.objects.get(
            periodic_task__name=periodic_task_name
        )
        if config.run_for_all_tenants:
            return list(
                OrganizationTenant.objects
                .filter(is_deleted=False, in_production=True)
                .exclude(schema_name='public')
                .values_list('schema_name', flat=True)
            )
        return list(config.tenants.values_list('schema_name', flat=True))
```

## 7. Canvas Primitives: `group` vs `chord`

### `group` — Parallel, Independent

All tasks fire simultaneously. No coordination. No callback. Use when per-tenant tasks are fully independent.

```
group([task(acme), task(globex), task(initech)]).delay()
    → all three fire at once, workers pick them up independently
```

### `chord` — Parallel + Callback

A `group` with a callback that fires **after all header tasks complete**. Requires a result backend (already satisfied by `django-celery-results`).

```
chord(
    group([task(acme), task(globex), task(initech)]),
    callback_task.si()   # fires only after all three are done
)
```

**Use `group` for:** independent per-tenant work (mark defaulted, send reminders).
**Use `chord` for:** "do all, then summarise" (generate all tenant reports, then email super-admin summary).

### `TenantFanOut` Wrapper

Centralises fan-out logic. Coordinators declare intent, not mechanics.

```python
class FanOutStrategy:
    PARALLEL      = "parallel"
    PARALLEL_THEN = "parallel_then"

class TenantFanOut:
    @staticmethod
    def execute(task, periodic_task_name, strategy=FanOutStrategy.PARALLEL, callback=None):
        schemas    = TenantPeriodicTaskWrapper.get_target_schemas(periodic_task_name)
        signatures = [task.si(schema_name=s) for s in schemas]

        if strategy == FanOutStrategy.PARALLEL:
            group(signatures).delay()
        elif strategy == FanOutStrategy.PARALLEL_THEN:
            chord(group(signatures), callback).delay()
```

Coordinator tasks become declarative:

```python
@app.task(name=TaskNames.COORDINATE_MARK_DEFAULTED,
          base=TenantAwareTask, failure_mode=FailureMode.ALERT)
def coordinate_mark_defaulted():
    TenantFanOut.execute(
        task=mark_defaulted_for_tenant,
        periodic_task_name=TaskNames.COORDINATE_MARK_DEFAULTED,
        strategy=FanOutStrategy.PARALLEL,
    )
```

## 8. Celery Beat — Detailed Execution Flow

Understanding this prevents misuse of Beat.

```
1. Beat starts
   → DatabaseScheduler loads ALL PeriodicTask rows into memory
   → builds in-memory heap sorted by next_run_time

2. Tick loop (runs continuously)
   → Is any task's next_run_time <= now?
       YES → send message to broker queue
           → update last_run_at in DB
           → recalculate next_run_time, re-insert into heap
       NO  → sleep(until_next_task)

3. DB sync (every ~5 seconds)
   → re-reads changed PeriodicTask rows
   → updates in-memory heap
   → enables runtime Admin changes without restarting Beat

4. Worker (separate process, polling broker)
   → sees message: { "task": "bma.periodic.coordinate_mark_defaulted", "kwargs": {} }
   → imports task function by dotted name string
   → calls task.__call__(**kwargs)
   → your Python code runs here
```

**Critical insight:** Beat does not execute tasks. It sends a message to the broker and its job ends. It has no knowledge of whether the worker succeeded or failed. Beat and workers are fully decoupled through the broker.

## 9. Docker Deployment

```yaml
services:
  valkey-cache:
    image: valkey/valkey

  valkey-broker:
    image: valkey/valkey
    command: valkey-server --appendonly yes # persistence enabled

  worker-fast:
    command: celery -A config worker -Q fast -c 4
    deploy:
      replicas: 2 # scale freely

  worker-heavy:
    command: celery -A config worker -Q heavy -c 2
    deploy:
      replicas: 3 # scale freely

  worker-scheduled:
    command: celery -A config worker -Q scheduled -c 1
    deploy:
      replicas: 1 # coordinator tasks are lightweight

  beat:
    command: celery -A config beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
    deploy:
      replicas: 1 # NEVER scale — singleton by design
```

**Beat singleton rule:** Two Beat instances reading the same DB schedule will both fire the same tasks. Every periodic job runs twice. There is no built-in distributed lock in Beat — the singleton is the only safe guarantee.

## 10. Configuration Location

Follows the project's existing `config/` convention.

```
config/
|- celery.py         # Celery app instance, autodiscover_tasks
|- celery_config.py  # Beat schedule, queue routing, serializer settings
```

```python
# config/celery.py
app = Celery('bma')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks([
    'project_apps.tasks.invoice_tasks',
    'project_apps.tasks.notification_tasks',
    'project_apps.tasks.periodic_tasks',
])
```

## 11. Things to remember in a Async Task

|     What to use       |           To avoid what           |
| --------------------- | --------------------------------- |
| select_for_update()   | Concurrent writes to same DB      |
| Idempotency guards    | Duplicate task execution          |
| Deterministic task_id | Duplicate task dispatch           |
| Cache lock            | External API calls, rate limiting | 

## 12. What's Not Yet Designed


| Item | Status | Notes |
| ---- | ------ | ----- |
| `notify_admin` util | Deferred | Called by `_handle_alert` and `_handle_dlq`. Needs Sentry/email implementation. |
| Task testing strategy | Deferred | How `TenantAwareTask` behaves with `task_always_eager` in tests. |
| Monitoring | Deferred | Flower for worker visibility + `django-celery-results` Admin. |

## Summary: All Finalised Decisions

| Concern | Decision |
| ------- | -------- |
| Broker | Two Valkey containers (cache / broker separated) |
| Result backend | `django-celery-results` (PostgreSQL) |
| Beat scheduler | `django-celery-beat` with `DatabaseScheduler` |
| Task location | Dedicated `project_apps/tasks/` module |
| Task discovery | Explicit `autodiscover_tasks` list |
| Task naming | Explicit names in `registry.py` with `bma.*` namespace |
| Queue routing | Pattern-based on task name prefix (zero-maintenance) |
| Tenant context | Custom `TenantAwareTask` base class (no external library) |
| Failure handling | Three-tier: SILENT / ALERT / DLQ via Strategy Pattern |
| DLQ replay | `DeadLetterEntry` model + replay API endpoint |
| Periodic tenant config | `TenantPeriodicTaskConfig` via Composition + ManyToMany |
| Fan-out primitive | `group` (independent) / `chord` (parallel + callback) |
| Fan-out wrapper | `TenantFanOut.execute()` with `FanOutStrategy` |
| Beat deployment | Singleton container, never scaled |
