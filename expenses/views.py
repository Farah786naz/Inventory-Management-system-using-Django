from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from users.permissions import IsAdminUser, IsManagerUser, IsStaffUser
from rest_framework.permissions import AllowAny
from .models import Expense
from .serializers import ExpenseSerializer



class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related('logged_by').all().order_by('-expense_date', '-created_at')
    serializer_class = ExpenseSerializer
    permission_classes = [AllowAny]
    
   

    """def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsAdminUser]
        elif self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAdminUser | IsManagerUser]
        else:
            permission_classes = [IsAdminUser | IsManagerUser | IsStaffUser]

        return [permission() for permission in permission_classes]"""

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)