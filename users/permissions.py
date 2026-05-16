from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Full system authorization. Can execute all operations."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'role') and 
            request.user.role == 'admin'
        )

class IsManagerUser(permissions.BasePermission):
    """Manager level authorization."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'role') and 
            request.user.role == 'manager'
        )

class IsStaffUser(permissions.BasePermission):
    """Baseline entry level staff authorization."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'role') and 
            request.user.role == 'staff'
        )