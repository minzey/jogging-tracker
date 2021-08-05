from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import FitnessUser
from .serializers import FitnessStaffSerializer, FitnessUserSerializer
from .permissions import IsUserManagerOrAdmin, IsRegularAndOwner


class AuthRoles(APIView):
    permission_classes = (IsUserManagerOrAdmin,)

    def get(self, request):
        response_dict = dict()
        for value, label in FitnessUser.Role.choices:
            response_dict[value] = label
        return JsonResponse(response_dict)


class RegisterUsers(generics.CreateAPIView):

    serializer_class = FitnessUserSerializer
    SUCCESSFUL_REGISTRATION_MESSAGE = 'Registration successful! Now you can use the login API'

    def post(self, request, *args, **kwargs):
        request.data['role'] = FitnessUser.Role.USER
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({'detail': self.SUCCESSFUL_REGISTRATION_MESSAGE}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows CRUD operations on user object that belongs to logged in user. No auth role changes allowed.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = FitnessUserSerializer
    queryset = FitnessUser.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        return obj

class UserViewSet(viewsets.ModelViewSet):
    """
    API to CRUD users:
    User Managers and Admins can create, retrieve, list, update, assign roles, and delete any user record with a
    lower or less privileged role
    """
    permission_classes = (IsUserManagerOrAdmin,)
    serializer_class = FitnessStaffSerializer
    # def get_serializer_class(self):
    #     if self.request.user.role == FitnessUser.Role.USER.value:
    #         return FitnessUserSerializer
    #     else:
    #         return FitnessStaffSerializer
    # todo: list, retrieve, and delete records accessible to logged in user's role. Add pagination and filter to list view

    def get_queryset(self):
        all_users = FitnessUser.objects.all()

        if self.request.user.role == FitnessUser.Role.ADMIN:
            return all_users

        else:
            # only return regular users and user managers
            return all_users.filter(role__lt=FitnessUser.Role.ADMIN)
