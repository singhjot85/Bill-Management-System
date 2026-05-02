# Bill Management Application
A system that can be used to generate and manage bills/invoices.

## Current Items in Scope (Raw Requirements):
- A user visits the webpage and can pay a certain amount to the vendor providing the link.
    - User has to enter a minimal data form, and pay using a payment gateway (Future scope user can generate bill without paying).
    - User gets invoice for the payment they made.
- A frequent visitor/known user can login and perform same functionalities but with enhanced features available to them.
- A BackOffice (BO) user can review, manage and generate invoivces.

## User Views:
- Public User:
    - Role: Public
    - Resposibilities: Can enter data, make payments, request bills, review their bills.
- Private User:
    - Role: Private
    - Resposibilities: Can login, enter data, make payments, request bills, review their bills.
- Tenant Admin:
    - Role: Manager (Current Tenant's Admin).
    - Resposibilities: Can login, enter data, make payments, request bills, review everyone's bills.
- Platform Admin:
    - Role: Project Admin
    - Resposibilities: Can login, manage tenants, configure new tenants.


## Tech Stack
**Backend:** django, djangorestframework, django-tenats + django-celery, django-celery-beat, valkey
**Frontend:** Vue + Vite
**Database:** PostgreSQL
**Other Infra:** Docker, Compose, Poetry, PreCommit
