from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
# Create your views here.

from .models import Product, Category, Supplier
from .serializers import ProductSerializer, CategorySerializer, SupplierSerializer
from rest_framework import viewsets
from django.db import models
from users.permissions import IsAdminUser, IsManagerUser, IsStaffUser

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    def get_permissions(self):
        # 1. Deleting a product requires Admin
        if self.action == 'destroy':
            permission_classes = [IsAdminUser]
        # 2. Creating or updating requires Admin OR Manager
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAdminUser | IsManagerUser]
        # 3. Viewing the product catalog is open to all authenticated roles
        else:
            permission_classes = [IsAdminUser | IsManagerUser | IsStaffUser]
            
        return [permission() for permission in permission_classes]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class ProductViewSet(viewsets.ModelViewSet):
    # Only expose active products by default (Soft-delete filter)
    queryset = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ProductSerializer
    
    # Simple search setup: allows typing /api/products/?search=keyboard
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sku', 'barcode']

    # Custom Low Stock API Endpoint: /api/products/low-stock/
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        # Filter products where current stock is less than or equal to threshold
        low_stock_items = Product.objects.filter(
            is_active=True, 
            stock_quantity__lte=models.F('low_stock_threshold')
        )
        serializer = self.get_serializer(low_stock_items, many=True)
        def get_permissions(self):
        # 1. Deleting a product requires Admin
            if self.action == 'destroy':
                permission_classes = [IsAdminUser]
            # 2. Creating or updating requires Admin OR Manager
            elif self.action in ['create', 'update', 'partial_update']:
                permission_classes = [IsAdminUser | IsManagerUser]
            # 3. Viewing the product catalog is open to all authenticated roles
            else:
                permission_classes = [IsAdminUser | IsManagerUser | IsStaffUser]
                
            return [permission() for permission in permission_classes]
        return Response(serializer.data)
    