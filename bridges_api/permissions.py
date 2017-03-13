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

class IsOwnerOrCreateOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers the ability to
    make GET requests
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user
        return True
