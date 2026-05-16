from django.db import models
from django.utils import timezone
from products.models import Product
from users.models import User
class StockMovement(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=50)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='stock_adjustments'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'stock_movements'
        indexes = [
            models.Index(fields=['product'], name='idx_stock_movements_prod_id'),
        ]