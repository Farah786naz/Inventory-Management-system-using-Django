from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import StockMovement, Product
from .serializers import StockMovementSerializer
from users.permissions import IsAdminUser, IsManagerUser, IsStaffUser

class StockMovementViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = StockMovement.objects.all().order_by('-created_at')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAdminUser | IsManagerUser ]

    def perform_create(self, serializer):
        with transaction.atomic():
            product = serializer.validated_data['product']
            qty = serializer.validated_data['quantity']
            movement_type = serializer.validated_data['movement_type']
            
            prev_stock = product.stock_quantity
            
            # Handle standard manual inventory adjustments
            if movement_type in ['restock', 'return']:
                new_stock = prev_stock + abs(qty)
            elif movement_type in ['damaged', 'lost', 'adjustment']:
                new_stock = prev_stock - abs(qty)
            else:
                new_stock = prev_stock + qty # Fallback processing logic
                
            product.stock_quantity = new_stock
            product.save()
            
            serializer.save(
                previous_stock=prev_stock,
                new_stock=new_stock,
                created_by=self.request.user
            )