from bma.requests.models import Bill
from bma.requests.serializers import BillSerializer
from rest_framework.viewsets import ModelViewSet


class BillViewSet(ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer


# response = HttpResponse(pdf_content, content_type='application/pdf')
# response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
