---
name: invoice-generation
description: Generate invoices from command line. Use when user asks to "create an invoice", "bill a customer", or "generate invoice number".
---

# Invoice Generation

When active:
1. Gather customer-id, amount, optional template-key
2. Run `python scripts/generate_invoice.py --customer-id 123 --amount 5000.00`
3. Confirm tenant invoice number (INV-YYYY-NNNN) and async PDF task ID
4. PDF generated asynchronously via Celery
