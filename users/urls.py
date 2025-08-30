from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.views.decorators.cache import cache_page

from users.apps import UsersConfig
from django.urls import path, include

from users.views import UserCreateView, verify_phone, UserViewSet, CustomLogoutView, PaymentListView, \
    payment_api_view, payment_success
from users.views import payment_page

router = SimpleRouter()
router.register(r'users', UserViewSet)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("verify-phone/",verify_phone, name="verify-phone"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('payment/', payment_page, name='payment_page'),
    path('api/', include(router.urls)),
    path("payments/", PaymentListView.as_view(), name="payment_list"),
    path("payment_api/", payment_api_view, name="payment_api"),
    path('api/', include(router.urls)),
    path('payment-success/', payment_success, name='payment_success'),
    # path("payments_create/", PaymentCreateAPIView.as_view(), name="payments_create"),
]