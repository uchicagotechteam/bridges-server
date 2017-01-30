from rest_framework import permissions

class MustBeSuperUserToGET(permissions.BasePermission):
    """
    Custom permission to only allow superusers the ability to
    make GET requests
    """
    def has_permission(self, request, view):
        if request.method == 'GET' and not request.user.is_superuser:
            return False
        return True
