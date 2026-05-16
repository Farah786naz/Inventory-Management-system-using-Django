from django.db import models
from sales.models import Sale
from django.utils import timezone

# Create your models here.
class Invoice(models.Model):
    id = models.BigAutoField(primary_key=True)
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='invoice')
    pdf_url = models.TextField(blank=True, null=True)
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'invoices'