from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from django.urls import path, include

from users.views import UserCreateView, verify_phone, UserViewSet, CustomLogoutView

router = SimpleRouter()
router.register(r'users', UserViewSet)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("verify-phone/", verify_phone, name="verify-phone"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]