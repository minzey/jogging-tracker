from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from rest_framework.response import Response

from .models import FitnessUser
from .serializers import FitnessUserSerializer, FitnessRegularUserSerializer
from .permissions import IsUserManagerOrAdmin, IsRegularAndOwner


class RegisterRegularUsers(generics.CreateAPIView):

    def post(self, request, *args, **kwargs):
        request.data['role'] = FitnessUser.Role.REGULAR
        serializer = FitnessRegularUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({'message': 'Registration successful! Now you can use the login API'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    API to CRUD users:
    1. Regular users can only retrieve, update and delete their own user
    2. User Managers and Admins can create, retrieve, list, update, assign roles, and delete any user record
    """
    queryset = FitnessUser.objects.all()
    permission_classes = (IsRegularAndOwner | IsUserManagerOrAdmin,)

    def get_serializer_class(self):
        if self.request.user.role == FitnessUser.Role.REGULAR.value:
            return FitnessRegularUserSerializer
        else:
            return FitnessUserSerializer
