# Bill Management Application
A system that can be used to generate and manage bills/invoices.

## Raw DB table requirements:
- Authentcated user records
- Non-Authenticated user records
- Invoice
- Invoice Template

## Fields to store and Model layouts
- Authenticated User:
    - Let Django Users handle it.
- Non-Authenticated user records (Customer Model):
    - name
    - phone
    - email
    - address (FK)
    - is_phone_verified
    - is_email_verified
- Invoices:
    - unique_identifier
    - docuemnt_url (File field)
    - context_data
    - invoice_template (FK)
- Invoive Template:
    - template_name
    - template_key
    - template_html
    - template_plain_text
