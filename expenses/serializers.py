from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    # 🟢 Mark this as read-only so the frontend doesn't have to send it
    logged_by_name = serializers.CharField(source='logged_by.full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = ['id', 'title', 'category', 'amount', 'description', 'expense_date', 'logged_by', 'logged_by_name', 'created_at']
        extra_kwargs = {
            'logged_by': {'read_only': True}
        }