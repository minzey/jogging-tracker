import json

from django.http import HttpRequest
from rest_framework import exceptions
from rest_framework.test import force_authenticate, APIRequestFactory

from userapi.serializers import FitnessUserSerializer, FitnessStaffSerializer
from userapi.tests import SerializerTest, BaseAPIViewTest, BaseEndToEndAPIViewTesting
from .serializers import JogRecordSerializer
from .views import JogList, JogDetail


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


class JogAPIViewTest(BaseAPIViewTest):

    def user_create_jog(self, user=None, token=None, user_data=None):
        if user is None or token is None:
            user_data = self.TEST_DATA

        user, token = self.get_user_header(user_data)

        data = {'date': '2021-08-09', 'location': 'New York', 'weather': 'Partly cloudy', 'jogger': user.id}

        request = APIRequestFactory().post('api/jogging/jogs/', data=data)
        force_authenticate(request, user=user, token=token)

        response = JogList.as_view()(request).render()
        content = eval(response.content.decode())

        return response, content

    def test_user_create_jog(self, user=None, token=None, user_data=None):
        response, content = self.user_create_jog(user=user, token=token, user_data=user_data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(content['id'])
        self.assertIsNotNone(content['weather'])

        return content['id']

    def user_get_jog(self, jog_id=None, user=None, token=None, user_data=None):
        if not jog_id:
            _, content = self.user_create_jog(user_data=user_data)
            jog_id = content['id']
            user = self.user
            token = self.token

        request = APIRequestFactory().get('api/jogging/jogs/')
        force_authenticate(request, user, token)

        response = JogDetail.as_view()(request, pk=jog_id).render()
        content = eval(response.content.decode())
        return response, content

    def test_user_get_jog(self, jog_id=None, user=None, token=None, user_data=None):
        response, content = self.user_get_jog(jog_id=jog_id, user=user, token=token, user_data=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(content['id'])

    def user_update_jog(self, jog_id=None, user=None, token=None, user_data=None):
        if not jog_id:
            _, content = self.user_create_jog(user_data=user_data)
            jog_id = content['id']
            user = self.user
            token = self.token

        body = {'location': 'test',
                'distance': 20,
                'time': 20,
                'jogger_id': user.id,
                'date': '2021-08-09',
                }

        request = APIRequestFactory().patch('api/jogging/jogs/', data=body)
        force_authenticate(request, user, token)

        response = JogDetail.as_view()(request, pk=jog_id).render()
        content = eval(response.content.decode())

        return response, content

    def test_user_update_jog(self, jog_id=None, user=None, token=None, user_data=None):
        response, content = self.user_update_jog(jog_id=jog_id, user=user, token=token, user_data=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['location'], 'test')
        self.assertEqual(content['distance'], 20)
        self.assertEqual(content['time'], 20)

    def user_delete_jog(self, jog_id=None, user=None, token=None, user_data=None):
        if not jog_id:
            _, content = self.user_create_jog(user_data=user_data)
            jog_id = content['id']
            user = self.user
            token = self.user

        request = APIRequestFactory().delete('api/jogging/jogs/')
        force_authenticate(request, user, token)

        response = JogDetail.as_view()(request, pk=jog_id).render()
        return response

    def test_user_delete_jog(self, jog_id=None, user=None, token=None, user_data=None):
        response = self.user_delete_jog(jog_id=jog_id, user=user, token=token, user_data=user_data)
        self.assertEqual(response.status_code, 204)


class JogEndToEndAPIViewTesting(BaseEndToEndAPIViewTesting):
    def user_journey_integration_testing(self):
        data_1 = self.USER_DATA
        data_2 = self.TEST_DATA

        # CREATE USER 1
        user_1, token = self.create_user(data_1)
        # CREATE USER 2
        user_2, token_2 = self.create_user(data_2)

        # USER 1 CAN CRUD OWN JOG
        jog_id = JogAPIViewTest().test_user_create_jog(user_1, token)
        JogAPIViewTest().test_user_get_jog(jog_id, user_1, token)
        JogAPIViewTest().test_user_update_jog(jog_id, user_1, token)
        JogAPIViewTest().test_user_delete_jog(jog_id, user_1, token)

        # USER 1 CANNOT CRUD 2 USER JOG
        jog_id_2 = JogAPIViewTest().test_user_create_jog(user_2, token_2)
        response, _ = JogAPIViewTest().user_get_jog(jog_id_2, user_1, token)
        self.assertEqual(response.status_code, 403)
        response, _ = JogAPIViewTest().user_update_jog(jog_id_2, user_1, token)
        self.assertEqual(response.status_code, 403)
        response = JogAPIViewTest().user_delete_jog(jog_id_2, user_1, token)
        self.assertEqual(response.status_code, 403)