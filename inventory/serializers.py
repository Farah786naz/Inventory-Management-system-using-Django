from rest_framework import serializers
from .models import StockMovement

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'quantity', 
            'previous_stock', 'new_stock', 'reason', 'created_by', 
            'creator_name', 'reference_id', 'created_at'
        ]
        read_only_fields = ['id', 'previous_stock', 'new_stock', 'created_at']