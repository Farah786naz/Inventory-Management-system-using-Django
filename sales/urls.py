from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet, CustomerViewSet, SalesReportView
router = DefaultRouter()
router.register(r'sales', SaleViewSet, basename='sales')
router.register(r'customers', CustomerViewSet, basename='customers')

urlpatterns = [
    path('',include(router.urls)),
    path('reports/', SalesReportView.as_view(), name='sales-report'),
]
