from django.contrib.auth.views import LoginView
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (CabinetView, CustomLogoutView, PaymentListView, UserCreateView, UserViewSet, payment_api_view,
                         payment_page, payment_success, verify_phone)

router = SimpleRouter()
router.register(r"users", UserViewSet)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("cabinet/", CabinetView.as_view(), name="cabinet"),
    path("verify-phone/", verify_phone, name="verify-phone"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("payment/", payment_page, name="payment_page"),
    path("api/", include(router.urls)),
    path("payments/", PaymentListView.as_view(), name="payment_list"),
    path("payment_api/", payment_api_view, name="payment_api"),
    path("api/", include(router.urls)),
    path("payment-success/", payment_success, name="payment_success"),
    # path("payments_create/", PaymentCreateAPIView.as_view(), name="payments_create"),
]
