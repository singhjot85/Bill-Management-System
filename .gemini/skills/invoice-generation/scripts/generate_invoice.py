#!/usr/bin/env python
"""Generate invoice command"""
import json, sys
from datetime import datetime, timezone, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from customer_management.models import Customer
from payments_management.models import Invoice, InvoiceTemplate

class Command(BaseCommand):
    help = "Generate invoice for a customer"

    def add_arguments(self, parser):
        parser.add_argument("--customer-id", type=int, required=True)
        parser.add_argument("--amount", type=float, required=True)
        parser.add_argument("--template-key", default="default_invoice")
        parser.add_argument("--context", default="{}")
        parser.add_argument("--due-days", type=int, default=30)

    def handle(self, *args, **options):
        try:
            customer = Customer.objects.get(id=options["customer_id"])
        except Customer.DoesNotExist:
            self.stderr.write(f"Customer {options['customer_id']} not found")
            sys.exit(1)

        template = InvoiceTemplate.objects.filter(
            template_key=options["template_key"]
        ).first() or InvoiceTemplate.objects.get(template_key="default_invoice")

        year = datetime.now().year
        last = Invoice.objects.filter(
            tenant_invoice_number__startswith=f"INV-{year}-"
        ).order_by("-tenant_invoice_number").first()
        seq = int(last.tenant_invoice_number.split("-")[-1]) + 1 if last else 1
        inv_num = f"INV-{year}-{seq:04d}"

        ctx = json.loads(options["context"])
        ctx.update({
            "recipient_name": customer.name,
            "recipient_email": customer.email,
            "invoice_date": datetime.now().isoformat(),
        })

        with transaction.atomic():
            invoice = Invoice.objects.create(
                recipient=customer,
                invoice_template=template,
                payable_amount=options["amount"],
                tenant_invoice_number=inv_num,
                context_data=ctx,
                status="DRAFT",
                invoice_date=datetime.now().date(),
                due_date=datetime.now().date() + timedelta(days=options["due_days"]),
            )
            from payments_management.tasks import generate_invoice_pdf_task
            task = generate_invoice_pdf_task.delay(invoice.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Invoice {inv_num} created (ID: {invoice.id}, Task: {task.id})"
                )
            )
