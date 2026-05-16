from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from .models import Sale, Customer
from .serializers import SaleSerializer,CustomerSerializer, SalesReportSerializer
from core.mixins import SoftDeleteModelMixin
from rest_framework import status
from django.db.models import Sum, F, Count
from django.utils.dateparse import parse_date
import datetime
from .models import Sale, SaleItem
from rest_framework.views import APIView
from rest_framework.response import Response
from users.permissions import IsAdminUser, IsManagerUser, IsStaffUser

class SaleViewSet(mixins.CreateModelMixin, 
                  mixins.RetrieveModelMixin, 
                  mixins.ListModelMixin, 
                  viewsets.GenericViewSet):
    """
    We block Update and Destroy routines for sales data.
    Financial and ledger records must remain immutable.
    """
    queryset = Sale.objects.all().order_by('-created_at')
    serializer_class = SaleSerializer
    permission_classes = [IsAdminUser | IsManagerUser | IsStaffUser]
    

class CustomerViewSet(SoftDeleteModelMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('full_name')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

class SalesReportView(APIView):
    def get(self, request, format=None):
        # 1. Capture date range parameters (default to the last 30 days if blank)
        start_param = request.query_params.get('start_date')
        end_param = request.query_params.get('end_date')
        
        end_date = parse_date(end_param) if end_param else datetime.date.today()
        start_date = parse_date(start_param) if start_param else end_date - datetime.timedelta(days=30)

        # 2. Filter sales within the target timeline
        sales_queryset = Sale.objects.filter(created_at__date__range=[start_date, end_date])
        
        # 3. Compute baseline financial aggregates directly in the database
        totals = sales_queryset.aggregate(
            order_count=Count('id'),
            gross=Sum('total_amount'),
            tax_total=Sum('tax'),
            discount_total=Sum('discount')
        )
        
        # Guard against empty database sets returning None values
        total_orders = totals['order_count'] or 0
        gross_sales = totals['gross'] or 0.00
        total_tax = totals['tax_total'] or 0.00
        total_discount = totals['discount_total'] or 0.00
        net_sales = float(gross_sales) - float(total_discount)

        # 4. Calculate COGS by digging into the related items sold during this period
        items_queryset = SaleItem.objects.filter(sale__created_at__date__range=[start_date, end_date])
        
        # COGS calculation formulas link cost_price from the products table
        cogs_calculation = items_queryset.aggregate(
            total_cost=Sum(F('quantity') * F('product__cost_price'))
        )
        total_cogs = cogs_calculation['total_cost'] or 0.00
        gross_profit = float(net_sales) - float(total_cogs)

        # 5. Extract top 5 performing products ordered by volume
        top_items = (
            items_queryset.values('product_id', 'product__name')
            .annotate(
                quantity_sold=Sum('quantity'),
                total_revenue=Sum('subtotal')
            )
            .order_by('-quantity_sold')[:5]
        )
        
        top_products_data = [
            {
                "product_id": item['product_id'],
                "product_name": item['product__name'],
                "quantity_sold": item['quantity_sold'],
                "total_revenue": item['total_revenue']
            } for item in top_items
        ]

        # 6. Format and pass data through our layout serializer
        report_data = {
            "start_date": start_date,
            "end_date": end_date,
            "total_orders": total_orders,
            "gross_sales": gross_sales,
            "total_tax": total_tax,
            "total_discount": total_discount,
            "net_sales": net_sales,
            "total_cogs": total_cogs,
            "gross_profit": gross_profit,
            "top_products": top_products_data
        }
        
        serializer = SalesReportSerializer(report_data)
        self.permission_classes = [IsAdminUser | IsManagerUser]
        return Response(serializer.data, status=status.HTTP_200_OK)