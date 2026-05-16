from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone

class SoftDeleteModelMixin:
    """
    Overrides the destroy method to set is_active=False 
    instead of hard deleting the record from the database.
    """
    def destroy(self, request, *request_pk, **kwargs):
        instance = self.get_object()
        
        if hasattr(instance, 'is_active'):
            instance.is_active = False
            if hasattr(instance, 'deleted_at'):
                instance.deleted_at = timezone.now()
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response(
            {"detail": "This model does not support soft deletion."}, 
            status=status.HTTP_400_BAD_REQUEST
        )