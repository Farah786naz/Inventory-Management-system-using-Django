from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet,ProductForecastView

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/forecast/product/<str:product_name>/', ProductForecastView.as_view(), name='product-forecast'),
]