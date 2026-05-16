from django.db import transaction
from inventory.models import StockMovement
from invoices.models import Invoice
from .models import Sale, SaleItem, Customer
from products.models import Product
from rest_framework import serializers

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'cost_price', 'discount_amount', 'subtotal']
        # cost_price is read_only because the backend snapshots it dynamically from the Product table
        read_only_fields = ['id', 'cost_price', 'subtotal']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    sold_by_name = serializers.CharField(source='sold_by.full_name', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'invoice_number', 'customer', 'customer_name', 'total_amount', 
            'tax', 'discount', 'payment_method', 'payment_status', 
            'sold_by', 'sold_by_name', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'total_amount', 'created_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Use atomic transactions to ensure data consistency across tables
        with transaction.atomic():
            # 1. Calculate transaction unique details (e.g., auto-generating invoice numbers)
            import uuid
            validated_data['invoice_number'] = f"INV-{uuid.uuid4().hex[:8].upper()}"
            
            # 2. Extract calculations dynamically
            running_total = 0
            sale = Sale.objects.create(**validated_data)
            
            for item_data in items_data:
                product = item_data['product']
                qty = item_data['quantity']
                
                # Check stock availability
                if product.stock_quantity < qty:
                    raise serializers.ValidationError(
                        f"Insufficient stock for product: {product.name}. Available: {product.stock_quantity}"
                    )
                
                # Snapshot values at transaction time
                unit_price = item_data['unit_price']
                discount = item_data.get('discount_amount', 0.00)
                subtotal = (unit_price - discount) * qty
                running_total += subtotal
                
                # Create Sale Item entry
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    unit_price=unit_price,
                    cost_price=product.cost_price, # Critical: Snapshot past cost margins
                    discount_amount=discount,
                    subtotal=subtotal
                )
                
                # 3. Handle Stock Movements & Deductions
                prev_stock = product.stock_quantity
                new_stock = prev_stock - qty
                
                product.stock_quantity = new_stock
                product.save()
                
                StockMovement.objects.create(
                    product=product,
                    movement_type='sale',
                    quantity=-qty,
                    previous_stock=prev_stock,
                    new_stock=new_stock,
                    reason=f"System Sale Checkout: {sale.invoice_number}",
                    created_by=validated_data.get('sold_by'),
                    reference_id=sale.id
                )
            
            # Apply header discounts/taxes to the total field balance
            tax = validated_data.get('tax', 0.00)
            overall_discount = validated_data.get('discount', 0.00)
            sale.total_amount = (running_total + tax) - overall_discount
            sale.save()
            
            # 4. Generate Associated Invoice Stub
            Invoice.objects.create(sale=sale, pdf_url=f"https://supabase.storage/invoices/{sale.invoice_number}.pdf")
            
            return sale
        
from rest_framework import serializers

class ProductPerformanceSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    quantity_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

class SalesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    total_orders = serializers.IntegerField()
    gross_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_cogs = serializers.DecimalField(max_digits=10, decimal_places=2)
    gross_profit = serializers.DecimalField(max_digits=10, decimal_places=2)
    top_products = ProductPerformanceSerializer(many=True)