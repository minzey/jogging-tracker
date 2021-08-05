from rest_framework import serializers, exceptions

from .models import FitnessUser


class FitnessUserSerializer(serializers.ModelSerializer):
    """
    Serializer that cannot make edits to role. Role is by default REGULAR USER here.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = FitnessUser
        fields = ['id', 'username', 'password']

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class FitnessStaffSerializer(FitnessUserSerializer):
    """
    Serializer for handling User Manager and Admin role operations.
    """

    user_role = serializers.ReadOnlyField(source='get_role_label')
    role = serializers.IntegerField(write_only=True)

    class Meta:
        model = FitnessUser
        fields = ['id', 'username', 'password', 'user_role', 'role']

    def validate(self, attrs):
        logged_in_user = self.context['request'].user
        logged_in_user_role = logged_in_user.role

        role_in_request = attrs.get('role', 0)

        if logged_in_user_role < role_in_request:
            raise exceptions.PermissionDenied("You cannot create/update a user with a more privileged role than yours")

        return attrs