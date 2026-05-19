from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'amount', 'expense_date', 'logged_by', 'created_at')
    list_filter = ('category', 'expense_date', 'created_at')
    search_fields = ('title', 'category', 'description', 'logged_by__full_name', 'logged_by__email')
    ordering = ('-expense_date', '-created_at')