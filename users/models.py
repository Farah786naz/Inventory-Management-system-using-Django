from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.utils import timezone

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    firebase_uid = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=50, default='staff')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'users'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=['admin', 'manager', 'staff']),
                name='check_user_role'
            )
        ] 

    def __str__(self):
        return f"{self.full_name} ({self.role})"