from rest_framework import permissions
from .models import FitnessUser


class IsUserManagerOrAdmin(permissions.IsAuthenticated):
    """
    Custom permission to only allow User managers and Admins to perform CRUD operations
    """
    def has_permission(self, request, view):
        return bool(request.user.role in [FitnessUser.Role.USER_MANAGER.value, FitnessUser.Role.ADMIN.value])

    def has_object_permission(self, request, view, obj):

        return self.has_permission(request, view)

class IsRegularAndOwner(permissions.IsAuthenticated):
    """
    Custom permission to only allow Regulars users to perform RUD operation on their own user record
    """
    def has_permission(self, request, view):

        return bool(view.action in ['update', 'partial_update', 'destroy', 'retrieve'])

    def has_object_permission(self, request, view, obj):

        return bool(request.user.role == FitnessUser.Role.REGULAR.value and \
               obj.id == request.user.id)

