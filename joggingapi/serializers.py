from rest_framework import serializers, exceptions

from .models import JogRecord
from userapi.models import FitnessUser

from utils.weather_api import WeatherAPI

class JogRecordSerializer(serializers.ModelSerializer):


    jogger = serializers.CharField(required=False)

    class Meta:
        model = JogRecord
        fields = ('id', 'jogger', 'date', 'distance', 'time', 'location', 'weather')
        read_only_fields = ('weather',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['jogger_id'] = instance.jogger.id

        return data

    def validate(self, attrs):

        logged_in_user = self.context['request'].user
        logged_in_user_role = logged_in_user.role
        jogger_in_record = attrs.get('jogger', None)

        if jogger_in_record is None:
            attrs['jogger'] = logged_in_user
            return attrs

        else:
            try:
                jogger_in_record = FitnessUser.objects.get(id=jogger_in_record)
                attrs['jogger'] = jogger_in_record
            except FitnessUser.DoesNotExist:
                raise exceptions.NotFound(f"User with id = {jogger_in_record} not found!")

            if logged_in_user == jogger_in_record:
                return attrs

            if logged_in_user_role == FitnessUser.Role.ADMIN.value:
                return attrs

            if logged_in_user_role == FitnessUser.Role.MANAGER.value or logged_in_user_role == FitnessUser.Role.USER.value:
                raise exceptions.PermissionDenied("You are not allowed to CRUD jog records of other users")

    def get_weather_conditions(self, data):
        return WeatherAPI(location=data['location'], date=data['date']).get_weather_conditions()

    def create(self, validated_data):
        validated_data['weather'] = self.get_weather_conditions(validated_data)
        return JogRecord.objects.create(**validated_data)









