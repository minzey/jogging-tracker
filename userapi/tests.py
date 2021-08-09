import json

from django.http import HttpRequest
from django.test import TestCase
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt import views as jwt_views
from rest_framework.test import APITestCase, APIRequestFactory, APIClient, force_authenticate

from .models import FitnessUser
from .serializers import FitnessUserSerializer, FitnessStaffSerializer
from .views import RegisterUsers, UserDetail, UserViewSet

class SerializerTest(APITestCase):
    USER_DATA = {"username": "regularuser", "password": "regularuser"}
    MANAGER_DATA = {"username": "usermanager", "password": "usermanager", "role": 1}
    ADMIN_DATA = {"username": "admin", "password": "admin", "role": 2}

    TEST_DATA = {"username": "test", "password": "test"}
    DATA_TEST = {"username": "test", "password": "test"}

    def create_user(self, data=None):
        data = data if data else self.USER_DATA
        user = FitnessUserSerializer().create(data)
        return user

    def create_manager(self, data=None):
        data = data if data else self.MANAGER_DATA
        manager = FitnessStaffSerializer().create(data)
        return manager

    def create_admin(self, data=None):
        data = data if data else self.ADMIN_DATA
        admin = FitnessStaffSerializer().create(data)
        return admin

class UserSerializerTest(SerializerTest):

    def setUp(self):
        self.serializer = FitnessUserSerializer()
        self.serializer.context['request'] = HttpRequest()

    def test_user_creation(self):
        user = self.serializer.create(self.USER_DATA)
        self.assertIsInstance(user, FitnessUser)
        self.assertEqual(user.role, FitnessUser.Role.USER.value)
        self.assertEqual(user.username, self.USER_DATA.get('username'))
        self.assertEqual(user.check_password(self.USER_DATA.get('password')), True)

    def test_user_update(self):
        manager = self.create_manager()
        manager = self.serializer.update(manager, self.DATA_TEST)
        self.assertIsInstance(manager, FitnessUser)
        self.assertEqual(manager.role, FitnessUser.Role.MANAGER.value)
        self.assertEqual(manager.username, self.DATA_TEST.get('username'))
        self.assertEqual(manager.check_password(self.DATA_TEST.get('password')), True)

    def test_creating_user_assigns_user_role(self):
        user = FitnessUserSerializer().create(self.DATA_TEST)
        self.assertEqual(user.role, FitnessUser.Role.USER.value)


class StaffSerializerTest(SerializerTest):
    def setUp(self):
        self.serializer = FitnessStaffSerializer()
        self.serializer.context['request'] = HttpRequest()

    def test_manager_creation(self):
        user = self.serializer.create(self.MANAGER_DATA)
        self.assertIsInstance(user, FitnessUser)
        self.assertEqual(user.role, FitnessUser.Role.MANAGER.value)
        self.assertEqual(user.username, self.MANAGER_DATA.get('username'))
        self.assertEqual(user.check_password(self.MANAGER_DATA.get('password')), True)

    def test_admin_creation(self):
        user = self.serializer.create(self.ADMIN_DATA)
        self.assertIsInstance(user, FitnessUser)
        self.assertEqual(user.role, FitnessUser.Role.ADMIN.value)
        self.assertEqual(user.username, self.ADMIN_DATA.get('username'))
        self.assertEqual(user.check_password(self.ADMIN_DATA.get('password')), True)

    def test_manager_cannot_create_admin(self):
        manager = self.create_manager(self.MANAGER_DATA)
        self.serializer.context['request'].user = manager
        data = {'role': FitnessUser.Role.ADMIN.value}
        self.serializer.validate(data)
        self.assertRaisesMessage(PermissionDenied, "You cannot create a user with a more privileged role than yours",
                                 self.serializer.validate, data)

    def test_admin_can_update_user(self):
        admin = self.create_admin(self.ADMIN_DATA)
        self.serializer.context['request'].user = admin

        user = self.create_manager(self.USER_DATA)
        self.serializer.context['request'].id = user.id

        self.serializer.validate(self.TEST_DATA)
        self.serializer.update(user, self.DATA_TEST)

        self.assertEqual(user.role, FitnessUser.Role.USER.value)
        self.assertEqual(user.username, self.DATA_TEST.get('username'))
        self.assertEqual(user.check_password(self.DATA_TEST.get('password')), True)

    def test_manager_can_promote_user_to_manager(self):
        manager = self.create_manager(self.MANAGER_DATA)
        self.serializer.context['request'].user = manager

        user = self.create_user(self.USER_DATA)
        self.serializer.context['request'].id = user.id
        data = {'role': FitnessUser.Role.MANAGER.value}
        self.serializer.validate(data)
        self.serializer.update(user, data)

        self.assertEqual(user.role, FitnessUser.Role.MANAGER.value)
        self.assertEqual(user.username, self.USER_DATA.get('username'))
        self.assertEqual(user.check_password(self.USER_DATA.get('password')), True)

    def test_admin_can_promote_manager_to_admin(self):
        admin = self.create_admin(self.ADMIN_DATA)
        self.serializer.context['request'].user = admin

        manager = self.create_manager(self.MANAGER_DATA)
        self.serializer.context['request'].id = manager.id
        data = {'role': FitnessUser.Role.ADMIN.value}
        self.serializer.validate(data)
        self.serializer.update(manager, data)

        self.assertEqual(manager.role, FitnessUser.Role.ADMIN.value)
        self.assertEqual(manager.username, self.MANAGER_DATA.get('username'))
        self.assertEqual(manager.check_password(self.MANAGER_DATA.get('password')), True)


class BaseAPIViewTest(SerializerTest):
    def get_user_header(self, data=None):
        UserAPIViewTest().user_register_view(data=data)
        _, token = UserAPIViewTest().login(data=data)
        user = FitnessUser.objects.get(username=data.get('username'))

        self.user = user
        self.token = token

        return user, token

    def get_staff_header(self, data=None):
        UserAPIViewTest().staff_register_view_with_logged_in_admin(data=data)
        _, token = UserAPIViewTest().login(data=data)
        user = FitnessUser.objects.get(id=data.get('id'))

        self.user = user
        self.token = token

        return user, token


class UserAPIViewTest(BaseAPIViewTest):

    def user_register_view(self, data=None):
        if data is None:
            data = self.USER_DATA

        request = APIRequestFactory().post('/api/auth/register/', data=json.dumps(data), content_type="application/json")
        response = RegisterUsers.as_view()(request).render()
        content = response.content.decode()
        content = eval(content)

        return response,  content

    def test_user_register_view(self, data=None):
        response, content = self.user_register_view(data=data)
        self.assertEqual(response.status_code, 201)


    def staff_register_view_without_logging_in(self, data=None):
        if data is None:
            data = self.MANAGER_DATA

        request = APIRequestFactory().post('/api/auth/users/', data=json.dumps(data), content_type="application/json")
        response = UserViewSet.as_view(actions={'post': 'create'})(request).render()
        content = response.content.decode()
        content = eval(content)

        return response,  content

    def test_staff_register_view_without_logging_in(self, data=None):
        response, content = self.staff_register_view_without_logging_in(data=data)
        self.assertEqual(response.status_code, 401)

    def staff_register_view_with_logged_in_admin(self, data=None, role=None):
        if data is None or role is None:
            data = self.MANAGER_DATA
        elif role is not None:
            data = self.MANAGER_DATA
            data["role"] = role

        request = APIRequestFactory().post('/api/auth/users/', data=json.dumps(data), content_type="application/json")
        force_authenticate(request, user=self.create_admin(self.ADMIN_DATA))
        response = UserViewSet.as_view(actions={'post': 'create'})(request).render()
        content = response.content.decode()
        content = eval(content)

        return response,  content

    def test_staff_register_view_with_logged_in_admin(self, data=None):
        response, content = self.staff_register_view_with_logged_in_admin(data=data)
        self.assertEqual(response.status_code, 201)

    def get_admin_with_logged_in_as_user_manager(self, admin_data=None, manager_data=None):
        if manager_data is None:
            manager_data = self.MANAGER_DATA

        if admin_data is None:
            admin = self.create_admin(self.ADMIN_DATA)
            admin_id = admin.id
        else:
            admin_id = admin_data['id']

        request = APIRequestFactory().get('/api/auth/users/', content_type="application/json")
        force_authenticate(request, user=self.create_manager(manager_data))
        response = UserViewSet.as_view(actions={'get': 'retrieve'})(request, pk=admin_id).render()
        content = response.content.decode()
        content = eval(content)

        return response,  content

    def test_get_admin_with_logged_in_as_user_manager(self, admin_data=None, manager_data=None):
        response, content = self.get_admin_with_logged_in_as_user_manager(admin_data=admin_data, manager_data=manager_data)
        self.assertEqual(response.status_code, 404)



    def login(self, data=None):
        if data is None:
            data = self.USER_DATA
            self.user_register_view(data)
        request = APIRequestFactory().post('/api/login/', data=json.dumps(data), content_type="application/json")
        response = jwt_views.TokenObtainPairView.as_view()(request).render()
        content = response.content.decode()
        content = eval(content)

        return response, content['access']

    def test_login(self, data=None):
        response, access_token = self.login(data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(access_token)

        return access_token

    def user_get_user(self, user_id=None, user=None, token=None, user_data=None):
        if not user_id:
            _, content = self.user_register_view(user_data)
            user_id = content['id']
            token = self.login(user_data)
            user = FitnessUser.objects.get(pk=user_id)

        request = APIRequestFactory().get('api/auth/myaccount/', content_type='application/json')
        force_authenticate(request, user, token)

        response = UserDetail.as_view()(request).render()
        content = eval(response.content.decode())
        return response, content

    def test_user_get_user(self, user_id=None, user=None, token=None, user_data=None):
        response, content = self.user_get_user(user_id=user_id, user=user, token=token, user_data=user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(content['id'])

    #
    # def staff_get_user(self, user_id=None, user=None, token=None, user_data=None):
    #     if not user_id:
    #         _, content = self.user_register_view(user_data)
    #         user_id = content['id']
    #         token = self.login(user_data)
    #         user = FitnessUser.objects.get(pk=user_id)
    #
    #     request = APIRequestFactory().get('api/auth/users/', content_type='application/json')
    #     force_authenticate(request, user, token)
    #
    #     response = UserViewSet.as_view(actions={'get': 'retrieve'})(request, pk=user_id).render()
    #     content = eval(response.content.decode())
    #     return response, content
    #
    # def test_staff_get_user(self, user_id=None, user=None, token=None, user_data=None):
    #     response, content = self.staff_get_user(user_id=user_id, user=user, token=token, user_data=user_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNotNone(content['id'])
    #
    #
    def user_update_user(self, user_id=None, user=None, token=None, user_data=None):
        if not user_id:
            _, content = self.user_register_view(user_data)
            user_id = content['id']
            token = self.login(user_data)
            user = FitnessUser.objects.get(pk=user_id)

        request = APIRequestFactory().put('api/auth/myaccount/', data=json.dumps(self.TEST_DATA), content_type='application/json')
        force_authenticate(request, user, token)

        response = UserDetail.as_view()(request, pk=user_id).render()
        content = eval(response.content.decode())
        return response, content

    def test_user_update_user(self, user_id=None, user=None, token=None, user_data=None):
        response, content = self.user_update_user(user_id=user_id, user=user, token=token, user_data=user_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['username'], self.TEST_DATA.get("username"))

    # def staff_update_user(self, user_id=None, user=None, token=None, user_data=None):
    #     if not user_id:
    #         _, content = self.user_register_view(user_data)
    #         user_id = content['id']
    #         token = self.login(user_data)
    #         user = FitnessUser.objects.get(pk=user_id)
    #
    #     body = self.USER_UPDATE_DATA
    #
    #     request = APIRequestFactory().put('api/auth/users/', data=json.dumps(body), content_type='application/json')
    #     force_authenticate(request, user, token)
    #
    #     response = UserDetail.as_view()(request, pk=user_id).render()
    #     content = eval(response.content.decode())
    #     return response, content
    #
    # def test_staff_update_user(self, user_id=None, user=None, token=None, user_data=None):
    #     response, content = self.user_update_user(user_id=user_id, user=user, token=token, user_data=user_data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(content['username'], 'regularuserupdated')
    #
    #
    def user_delete_user(self, user_id=None, user=None, token=None, user_data=None):
        if not user_id:
            _, content = self.user_register_view(user_data)
            user_id = content['id']
            token = self.login(user_data)
            user = FitnessUser.objects.get(pk=user_id)

        request = APIRequestFactory().delete('api/auth/myaccount/', content_type='application/json')
        force_authenticate(request, user, token)

        response = UserDetail.as_view()(request, pk=user_id).render()
        return response

    def test_user_delete_user(self, user_id=None, user=None, token=None, user_data=None):
        response = self.user_delete_user(user_id=user_id, user=user, token=token, user_data=user_data)
        self.assertEqual(response.status_code, 204)

class BaseEndToEndAPIViewTesting(BaseAPIViewTest):

    def create_user(self, data):
        UserAPIViewTest().user_register_view(data)
        user = FitnessUser.objects.get(username=data.get('username'))
        token = UserAPIViewTest().test_login(data)

        return user, token

    def create_manager(self, data):
        UserAPIViewTest().staff_register_view_with_logged_in_admin(data, 1)
        manager = FitnessUser.objects.get(username=data.get('username'))
        token = UserAPIViewTest().test_login(data)
        return manager, token

    def create_admin(self, data):
        UserAPIViewTest().staff_register_view_with_logged_in_admin(data, 2)
        admin = FitnessUser.objects.get(username=data.get('username'))
        token = UserAPIViewTest().test_login(data)
        return admin, token

class UserEndToEndAPIViewTesting(BaseEndToEndAPIViewTesting):
    def user_journey_integration_testing(self):
        data_1 = self.USER_DATA
        data_2 = self.TEST_DATA

        # CREATE USER 1
        user_1, token = self.create_user(data_1)
        # CREATE USER 2
        user_2, token_2 = self.create_user(data_2)

        # USER 1 CAN CRUD HIS DATA
        UserAPIViewTest().test_user_get_user(user_1.pk, user_1, token)
        UserAPIViewTest().test_user_update_user(user_1.pk, user_1, token)
        UserAPIViewTest().test_user_delete_user(user_1.pk, user_1, token)

        # CREATE USER AGAIN
        user_1, token = self.create_user(data_1)

        # USER 1 CANNOT CRUD USER 2 DATA
        response, _ = UserAPIViewTest().user_get_user(user_2.pk, user_1, token)
        self.assertEqual(response.status_code, 403)
        response, _ = UserAPIViewTest().user_update_user(user_2.pk, user_1, token)
        self.assertEqual(response.status_code, 403)
        response = UserAPIViewTest().user_delete_user(user_2.pk, user_1, token)
        self.assertEqual(response.status_code, 403)

        ##### JOGGING

        # USER 1 CAN CRUD HIS JOG
        JogAPIViewTest().test_create_jog_without_logging_in(data)
        jog_id = JogAPIViewTest().test_user_create_jog(user, token)
        JogAPIViewTest().test_user_get_jog(jog_id, user, token)
        JogAPIViewTest().test_user_update_jog(jog_id, user, token)
        JogAPIViewTest().test_user_delete_jog(jog_id, user, token)

        # USER 1 CANNOT CRUD 2 USER JOG
        jog_id_2 = JogAPIViewTest().test_user_create_jog(user_2, token_2)
        response, _ = JogAPIViewTest().user_get_jog(jog_id_2, user, token)
        self.assertEqual(response.status_code, 403)
        response, _ = JogAPIViewTest().user_update_jog(jog_id_2, user, token)
        self.assertEqual(response.status_code, 403)
        response = JogAPIViewTest().user_delete_jog(jog_id_2, user, token)
        self.assertEqual(response.status_code, 403)