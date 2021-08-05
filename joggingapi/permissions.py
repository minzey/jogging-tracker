from rest_framework import permissions
from userapi.models import FitnessUser


class IsJogRecordOwnerOrStaff(permissions.IsAuthenticated):
    """
    Custom permission for accessing jog records
    """

    SAFE_METHODS = ['GET']

    def has_object_permission(self, request, view, obj):
        """
        Rules to access job objects:
        1. Authenticated users can access the records created by them.
        2. Admin users can access and change records created by any user.
        3. User managers can access and read records created by regular users and other user managers.
        """
        obj_user = obj.jogger

        if obj_user == request.user:
            return True

        user_auth_role = FitnessUser.get_auth_role(request.user.id)
        obj_auth_role = FitnessUser.get_auth_role(obj_user.id)

        if user_auth_role == FitnessUser.Role.ADMIN.value:
            return True

        if obj_auth_role == FitnessUser.Role.USER.value:
            if user_auth_role == FitnessUser.Role.ADMIN.value:
                return True

            elif user_auth_role == FitnessUser.Role.MANAGER.value and request.method in self.SAFE_METHODS:
                return True

        return False
