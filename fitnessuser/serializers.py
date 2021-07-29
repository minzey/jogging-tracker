from rest_framework import serializers

from .models import FitnessUser

class FitnessRegularUserSerializer(serializers.ModelSerializer):
    """
    Serializer that cannot made edits to role. Role is by default REGULAR here.
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


class FitnessUserSerializer(FitnessRegularUserSerializer):
    """
    Serializer for handling User Manager and Admin role operations.
    """

    user_role = serializers.ReadOnlyField(source='get_role_label', read_only=True)
    password = serializers.CharField(write_only=True)
    role = serializers.IntegerField(write_only=True)

    class Meta:
        model = FitnessUser
        fields = ['id', 'username', 'password', 'user_role', 'role']