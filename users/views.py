from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
# Create your views here.
from rest_framework import viewsets
from .models import User
from .serializers import Userserializer
from .permissions import IsAdminUser,IsManagerUser,IsStaffUser
class Userview(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Userserializer
    permission_classes = [IsAdminUser|IsManagerUser|IsStaffUser]

    def get_queryset(self):
        queryset = User.objects.all().order_by('id')
        firebase_uid = self.request.query_params.get('firebase_uid')

        if firebase_uid:
            queryset = queryset.filter(firebase_uid=firebase_uid)

        return queryset

    def get_permissions(self):
        """
        Allows anyone to make a POST request to /api/users/ (Signup) or GET list (for firebase_uid lookup).
        All other operations (Update, Delete) remain locked to admins/managers.
        """
        if self.action in ['create', 'list']:
            return [AllowAny()]
        return super().get_permissions()