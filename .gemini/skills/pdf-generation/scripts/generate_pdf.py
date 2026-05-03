#!/usr/bin/env python
"""PDF generation utility"""
import hashlib, base64
from io import BytesIO
from django.template.loader import render_to_string
from django.core.cache import cache
from django.core.files.base import ContentFile
from weasyprint import HTML
import qrcode

class InvoicePDFGenerator:
    def __init__(self, tenant_schema):
        self.tenant_schema = tenant_schema

    def generate(self, invoice):
        context = self._build_context(invoice)
        html = self._render_html(invoice, context)
        pdf = self._generate_pdf(html, invoice)
        return ContentFile(pdf, name=f"invoice_{invoice.tenant_invoice_number}.pdf")

    def _build_context(self, invoice):
        return {
            **invoice.context_data,
            "tenant_invoice_number": invoice.tenant_invoice_number,
            "invoice_date": invoice.invoice_date.strftime("%B %d, %Y"),
            "payable_amount": f"₹{invoice.payable_amount:,.2f}",
            "recipient_name": invoice.recipient.name,
            "status": invoice.status,
            "qr_code": self._generate_qr(invoice),
        }

    def _render_html(self, invoice, context):
        key = f"pdf_html:{self.tenant_schema}:{invoice.invoice_template_id}"
        html = cache.get(key)
        if not html:
            html = render_to_string("invoice_template.html", {"context": context})
            cache.set(key, html, 3600)
        return html

    def _generate_pdf(self, html, invoice):
        h = hashlib.md5(html.encode()).hexdigest()
        key = f"pdf:{self.tenant_schema}:{h}"
        pdf = cache.get(key)
        if not pdf:
            pdf = HTML(string=html).write_pdf(optimize_size=True)
            cache.set(key, pdf, 86400)
        return pdf

    def _generate_qr(self, invoice):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(f"/verify/{invoice.tenant_invoice_number}")
        qr.make(fit=True)
        buf = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(buf, "PNG")
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
