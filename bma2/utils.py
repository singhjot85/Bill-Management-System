import uuid
from io import BytesIO

import jq
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
from django.template.loader import get_template, render_to_string
from weasyprint import HTML
from xhtml2pdf import pisa

from bma.constants import PAYMENTS_TYPE_CHOICE_TO_MODEL_MAP as payment_model_map

"""
dependencies for weasyprint:
    brew install cairo pango gdk-pixbuf libffi
dependencies for xhtml2pdf:
    brew install cairo pkg-config
"""


def add_rendered_pdf_to_response(
    template: str,
    data: dict,
    response: HttpResponse = HttpResponse(),
    enhanced_styling: bool = True,
) -> HttpResponse:
    """
    Args:
        template (str): Template name.
        data (dict): Context for template.
        response (HttpResponse): Empty response object to be returned.
        enhanced_styling (bool): Using weasyprint achieves enhanced styling.
    """
    if enhanced_styling:
        complete_template = render_to_string(template, context=data)

        pdf_buffer = BytesIO()
        parser = HTML(string=complete_template)
        parser.write_pdf(pdf_buffer)

        pdf_buffer.seek(0)  # Move head to start
        response = HttpResponse(content=pdf_buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="invoice.pdf"'
        return response

    template = get_template(template)
    html = template.render(data)

    response = HttpResponse(content_type="application/pdf", status=200)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(content="We had some errors <pre>" + html + "</pre>", status=500)
    response["Content-Disposition"] = 'inline; filename="invoice.pdf"'
    return response


def generate_random_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid4()))


def phone_number_validator(number: str):
    cleaned_number = number.replace("-", "").replace(" ", "").strip()
    if len(cleaned_number) != 10:
        raise ValidationError("Phone number must have exactly 10 digits.")
    if not cleaned_number.isdigit():
        raise ValidationError("Phone number must contain only digits.")


def jq_transform_payload(input_payload: dict, jq_path: str):
    try:
        with open(jq_path) as f:
            jq_program = f.read()
        output_payload = jq.compile(jq_program).input(input_payload).first()
    except Exception as exc:
        return str(f"Error in jq tranformation [{str(exc)}]")

    return output_payload


def jq_transform_with_config(input_payload: dict, config: dict, jq_path: str):
    try:
        with open(jq_path) as f:
            jq_program = f.read()
        output_payload = jq.compile(jq_program, config).input(input_payload).first()
    except Exception as exc:
        return str(f"Error in jq tranformation [{str(exc)}]")

    return output_payload


def get_contenttype_for_payment(payment_mode: str):
    """
    Give a payment mode choice and this will return
    ContentType for that choice's corresponding model
    Args:
        payment_mode (str): Mode of payment from payment mode choices
    Returns:
        content_type : Content Type for that model
        Model : Model of the app
    """
    model_name = payment_model_map.get(payment_mode, None)
    if not model_name:
        raise Exception("Payment mode not supported yet.")
    Model = apps.get_model("payments", model_name)
    return ContentType.objects.get_for_model(Model), Model
