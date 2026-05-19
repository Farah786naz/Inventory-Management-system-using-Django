from django.db import models
from django.utils import timezone

from users.models import User


class Expense(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    expense_date = models.DateField(default=timezone.localdate)
    logged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='expenses_logged',
        db_column='logged_by',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.amount})"