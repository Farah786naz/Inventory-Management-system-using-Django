from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Invoice
from .serializers import InvoiceDetailSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.utils import timezone
import datetime
import math

from sales.models import SaleItem
from products.models import Product
from .serializers import ForecastResultSerializer

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
    



class ProductForecastView(APIView):
    # Change parameter from product_id to product_name
    def get(self, request, product_name):
        try:
            # Look up the product using case-insensitive exact name matching
            product = Product.objects.get(name__iexact=product_name, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"error": f"Active product with name '{product_name}' not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Product.MultipleObjectsReturned:
            return Response(
                {"error": f"Multiple products found with the name '{product_name}'. Please use a unique identifier."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Fetch sales history using the product object we just fetched
        ninety_days_ago = timezone.now() - datetime.timedelta(days=90)
        sales_data = SaleItem.objects.filter(
            product=product,  # Pass the product instance directly
            sale__created_at__gte=ninety_days_ago
        ).values('sale__created_at__date').annotate(total_qty=Sum('quantity'))

        # 2. If there is little to no sales history, return fallback logic
        if not sales_data or len(sales_data) < 5:
            return Response(self._generate_fallback_data(product), status=status.HTTP_200_OK)

        # 3. Build a daily sales series without relying on pandas.
        sales_by_date = {
            row['sale__created_at__date']: row['total_qty'] or 0
            for row in sales_data
        }
        start_date = min(sales_by_date)
        end_date = datetime.date.today()
        daily_quantities = []
        current_day = start_date
        while current_day <= end_date:
            daily_quantities.append(sales_by_date.get(current_day, 0))
            current_day += datetime.timedelta(days=1)

        # 4. Run forecasting metrics using an exponential moving average.
        ema_sales = []
        smoothing_factor = 2 / (14 + 1)
        for quantity in daily_quantities:
            if not ema_sales:
                ema_sales.append(float(quantity))
            else:
                ema_sales.append((quantity * smoothing_factor) + (ema_sales[-1] * (1 - smoothing_factor)))

        daily_burn_rate = float(ema_sales[-1])
        
        if daily_burn_rate <= 0:
            daily_burn_rate = 0.01 

        predicted_30_day_demand = int(math.ceil(daily_burn_rate * 30))
        
        # 5. Calculate Days Remaining until stock hits zero
        current_stock = product.stock_quantity
        estimated_days_out = int(math.floor(current_stock / daily_burn_rate))
        recommended_reorder = max(0, predicted_30_day_demand - current_stock)

        forecast_payload = {
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": current_stock,
            "predicted_30_day_demand": predicted_30_day_demand,
            "daily_burn_rate": round(daily_burn_rate, 2),
            "estimated_days_out": estimated_days_out,
            "recommended_reorder_quantity": recommended_reorder
        }

        serializer = ForecastResultSerializer(forecast_payload)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _generate_fallback_data(self, product):
        return {
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": product.stock_quantity,
            "predicted_30_day_demand": 0,
            "daily_burn_rate": 0.0,
            "estimated_days_out": 999,
            "recommended_reorder_quantity": 0
        }