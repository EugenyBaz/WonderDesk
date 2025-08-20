from django.contrib.auth.views import LoginView, LogoutView
from users.apps import UsersConfig
from django.urls import path

from users.views import UserCreateView, verify_phone

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page ="/"), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("verify-phone/", verify_phone, name="verify-phone"),
]