from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from fitnessuser import api


router = DefaultRouter()
router.register(r'users', api.UserViewSet)


urlpatterns = [
    path('register/', api.RegisterRegularUsers.as_view(), name='register_regular_users'),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls))
]