from django.http import HttpRequest
from rest_framework import exceptions

from userapi.serializers import FitnessUserSerializer, FitnessStaffSerializer
from userapi.tests import SerializerTest
from .serializers import JogRecordSerializer

class JogSerializerTest(SerializerTest):


    def setUp(self) -> None:
        self.serializer = JogRecordSerializer()
        self.serializer.context['request'] = HttpRequest()
        self.user = FitnessUserSerializer().create(self.USER_DATA)
        self.manager = FitnessStaffSerializer().create(self.MANAGER_DATA)
        self.admin = FitnessStaffSerializer().create(self.ADMIN_DATA)

    def test_jog_create(self):
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': self.user.id}
        self.serializer.context['request'].user = self.user
        jog = self.serializer.create(self.serializer.validate(data))

        self.assertEqual(jog.date, data.get('date'))
        self.assertEqual(jog.location, data.get('location'))
        self.assertEqual(jog.weather, data.get('weather'))
        self.assertEqual(jog.jogger.id, self.user.id)

    def test_jog_update(self):
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': self.user.id}
        self.serializer.context['request'].user = self.user
        jog = self.serializer.create(self.serializer.validate(data))
        new_data = {'location': 'London', 'weather': 'Rainy'}
        jog = self.serializer.update(jog, new_data)

        self.assertEqual(jog.date, data.get('date'))
        self.assertEqual(jog.location, new_data.get('location'))
        self.assertEqual(jog.weather, new_data.get('weather'))
        self.assertEqual(jog.jogger.id, self.user.id)

    def test_user_can_CRUD_jog_for_own(self):
        user = FitnessUserSerializer().create(self.TEST_DATA)
        self.serializer.context['request'].user = user
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': user.id}
        self.assertEqual(data, self.serializer.validate(data))

    def test_user_cannot_CRUD_jog_for_other_user(self):
        user = FitnessUserSerializer().create(self.TEST_DATA)
        self.serializer.context['request'].user = user
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': self.user.id}
        self.assertRaisesMessage(exceptions.PermissionDenied, "You are not allowed to CRUD jog records of other users",
                                 self.serializer.validate, data)

    def test_manager_cannot_CRUD_jog_for_other_user(self):
        self.serializer.context['request'].user = self.manager
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': self.user.id}
        self.assertRaisesMessage(exceptions.PermissionDenied, "You are not allowed to CRUD jog records of other users",
                                 self.serializer.validate, data)


    def test_admin_can_CRUD_jog_for_user(self):
        self.serializer.context['request'].user = self.admin
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': self.user.id}
        self.assertEqual(data, self.serializer.validate(data))

    def test_admin_can_CRUD_jog_for_manager(self):

        self.serializer.context['request'].user = self.admin
        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': self.manager.id}
        self.assertEqual(data, self.serializer.validate(data))
