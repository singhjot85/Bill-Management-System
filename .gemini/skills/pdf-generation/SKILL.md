---
name: pdf-generation
description: Generate PDF invoices and receipts using WeasyPrint. Use when user asks to "create PDF", "design template", or "generate receipt".
---

# PDF Generation

When active:
1. Use InvoicePDFGenerator from scripts/generate_pdf.py
2. Templates cached in Valkey (1 hour)
3. PDFs cached by content hash (24 hours)
4. QR codes generated for verification
5. All generation async via Celery
