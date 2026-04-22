# Bill Management Application
A system that can be used to generate and manage bills/invoices.

## Raw DB table requirements:
- Authentcated user records
- Non-Authenticated user records
- Invoice
- Invoice Template

## Fields to store and Model layouts
All models will implement SoftDelete + TimeStamp mixins. Not written below to reduce boilerplate.


### Authenticated User

- Use Django default user model (`django.contrib.auth`) for authenticated users.

---

### Non-Authenticated User Records (`Customer` Model)

- name
- phone
- email
- is_phone_verified
- is_email_verified
- source
- customer_type  
  (`PUBLIC / PRIVATE / VIP / CORPORATE`)
- external_reference
- details (JSON)

#### Relationships

- addresses (1:M → CustomerAddress)
- invoices (1:M → Invoice)
- payments (1:M → Payment)

---

### Customer Address (`CustomerAddress` Model)

- customer (FK → Customer)
- address_line_1
- address_line_2
- city
- state
- country
- postal_code
- is_primary

---

### Invoices (`Invoice` Model)

- invoice_date
- due_date
- status
- tenant_invoice_number  
  (Example: `INV-2026-0001`)
- document_url (FileField)
- context_data (JSON)
- payable_amount
- amount_paid

#### Relationships

- recipient (FK → Customer)
- invoice_template (FK → InvoiceTemplate)
- generated_by (FK → AUTH_USER_MODEL)

### Reverse Relations

- payments (1:M ← Payment)

> Removed direct `payment` field from Invoice model to avoid duplication.  
> Payments should always reference Invoice from the Payment model.

---

### Invoice Template (`InvoiceTemplate` Model)

- template_name
- template_key
- template_html
- template_plain_text
- is_active
- versioning

#### Relationships

- invoices (1:M ← Invoice)

---

### Payments (`Payment` Model)

- status
- payment_type
- order_id
- payment_id
- amount
- currency
- details (JSON)
- raw_payment_responses (JSON)
- verified_on (DateTime)
- gateway_name
- gateway_signature
- verified_flag

#### Relationships

- payee (FK → Customer)
- invoice (FK → Invoice)
- verified_by (FK → AUTH_USER_MODEL)

> Removed duplicate M:M reference between Payment and Invoice.  
> Correct relationship is: One Invoice → Many Payments

---

## Django Apps and Models

### auth
- `django.contrib.auth`

### customer_management
- customer
- customer_address

### payments_management
- invoice
- invoice_template
- payment

---

## Django Tenants Reference:
```text
tenants/ -> Public Schema

customer_management/ -> Tenant Scoped
payments_management/ -> Tenant Scoped
setup/ -> Tenant Scoped
```


## Foreign Key Refernces:
```
CustomerAddress -> Customer (M:1)
customer = ForeignKey(to=Customer)

Invoice -> Customer (M:1)
recipient = ForeignKey(to=Customer)

Payment -> Invoice (M:1)
invoice = ForeignKey(to=Invoice)

Invoice -> InvoiceTemplate (M:1)
invoice_template = ForeignKey(to=InvoiceTemplate)

Payment -> Customer (M:1)
payee = ForeignKey(to=Customer)

Invoice -> GeneratedBy (M:1)
generated_by = ForeignKey(to=AUTH_USER_MODEL)

Payment -> VerifiedBy (M:1)
verified_by = ForeignKey(to=AUTH_USER_MODEL)
```