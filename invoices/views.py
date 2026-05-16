from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Invoice
from .serializers import InvoiceDetailSerializer

class InvoiceViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    Read-only viewset for auditing and downloading financial invoices.
    """
    queryset = Invoice.objects.all().select_related('sale', 'sale__customer', 'sale__sold_by').order_by('-generated_at')
    serializer_class = InvoiceDetailSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='download')
    def download_pdf(self, request, pk=None):
        """
        Custom endpoint to fetch the actual file attachment.
        Path: /api/invoices/<id>/download/
        """
        invoice = self.get_object()
        
        if invoice.pdf_url:
            # Redirect the mobile/web client directly to the secure cloud file storage destination
            return HttpResponseRedirect(invoice.pdf_url)
            
        return Response(
            {"detail": "PDF file artifact has not been generated for this invoice transaction record yet."},
            status=status.HTTP_404_NOT_FOUND
        )