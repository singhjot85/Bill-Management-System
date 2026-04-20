from django.contrib import admin

from bma.requests.models import Bill

DEFAULT_TEMPLATE_PATH = r"test_invoice.html"

# @admin.action(description="Download Multiple Bills as a ZPF file")
# def download_pdf_zip(modeladmin, request, queryset):

#     if len(queryset) < 1:
#         messages.error(request, "ERROR - No objects selcted !!")

#     template_path = DEFAULT_TEMPLATE_PATH
#     zip_buffer = BytesIO()
#     with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
#         for obj in queryset:
#             serialized_data = BillSerializer(obj)
#             if serialized_data.is_valid:
#                 pdf_buffer = render_to_pdf(template_path, serialized_data.data)
#                 pdf_buffer.seek(0)
#                 filename = f"bill_{serialized_data.data.get("name", "")}.pdf"
#                 zip_file.writestr(filename, pdf_buffer.read())
#             else:
#                 error_msg = str(serialized_data.errors)
#                 messages.error(request, f"ERROR - Bill [{obj}] is invalid, {error_msg}")

#         zip_buffer.seek(0)

#     response = HttpResponse(zip_buffer, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="bills.zip"'

#     return response

# @admin.action(description="Download Single Bills as a PDF file")
# def download_pdf(modeladmin, request, queryset):

#     if len(queryset) > 1:
#         messages.error(request, "ERROR - Mutliple objects selcted !!")
#     if len(queryset) < 1:
#         messages.error(request, "ERROR - No objects selcted !!")

#     obj = queryset.first()
#     serialized_data = BillSerializer(obj)

#     if serialized_data.is_valid:
#         template_path = DEFAULT_TEMPLATE_PATH
#         pdf_buffer = render_to_pdf(template_path, serialized_data.data)
#         pdf_buffer.seek(0)
#         response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="{serialized_data.field_name}.pdf"'
#         return response
#     else:
#         error_msg = str(serialized_data.errors)
#         messages.error(request, f"ERROR - Bill is invalid {error_msg}")


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "total_amount")
    list_filter = ["state", "currency"]
    search_fields = ("name", "state", "total_amount")
    actions = [
        # download_pdf,
        # download_pdf_zip
    ]
