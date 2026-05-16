from rest_framework import serializers
from .models import Invoice
from sales.models import Sale, SaleItem

class InvoiceSaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['product_name', 'sku', 'quantity', 'unit_price', 'discount_amount', 'subtotal']

class InvoiceDetailSerializer(serializers.ModelSerializer):
    # Trailing fields fetched via database relationships
    customer_name = serializers.CharField(source='sale.customer.full_name', read_only=True)
    customer_email = serializers.CharField(source='sale.customer.email', read_only=True)
    customer_phone = serializers.CharField(source='sale.customer.phone', read_only=True)
    customer_address = serializers.CharField(source='sale.customer.address', read_only=True)
    
    invoice_number = serializers.CharField(source='sale.invoice_number', read_only=True)
    total_amount = serializers.DecimalField(source='sale.total_amount', max_digits=10, decimal_places=2, read_only=True)
    tax = serializers.DecimalField(source='sale.tax', max_digits=10, decimal_places=2, read_only=True)
    discount = serializers.DecimalField(source='sale.discount', max_digits=10, decimal_places=2, read_only=True)
    payment_method = serializers.CharField(source='sale.payment_method', read_only=True)
    payment_status = serializers.CharField(source='sale.payment_status', read_only=True)
    sold_by_name = serializers.CharField(source='sale.sold_by.full_name', read_only=True)
    
    # Nested line items
    items = InvoiceSaleItemSerializer(source='sale.items', many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'sale', 'invoice_number', 'pdf_url', 'generated_at',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'total_amount', 'tax', 'discount', 'payment_method', 'payment_status',
            'sold_by_name', 'items'
        ]
        read_only_fields = ['__all__']