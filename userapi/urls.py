from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from userapi import views


router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename="FitnessUser")


urlpatterns = [
    # CRUD URLs for staff
    path('', include(router.urls)),
    path('roles/', views.AuthRoles.as_view(), name='auth_roles'),

    # CRUD URLs for regular users
    path('register/', views.RegisterUsers.as_view(), name='register_users'),
    path('myaccount/', views.UserDetail.as_view(), name='user_detail'),

    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),


]