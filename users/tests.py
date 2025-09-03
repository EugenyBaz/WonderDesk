import uuid
from unittest.mock import patch
from django.http import HttpResponseRedirect
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from posts.models import Post
from users.forms import UserRegisterForm
from users.models import User
from users.views import UserCreateView


class TestCabinetView(TestCase):

    def setUp(self):
        self.user = User.objects.create(phone_number="+791111111111")
        self.post = Post.objects.create(title="Test Post", description="Пост создан для теста", author=self.user)

        self.client = Client()

    def test_cabinet_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:cabinet"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Личный кабинет")


class UserCreateViewTest(TestCase):
    def setUp(self):
        # Заводим фабрику запросов
        self.factory = RequestFactory()

    def test_create_user_and_verify_phone(self):
        # Подготавливаем фиктивную форму
        form_data = {
            "phone_number": "+79111111111",
            "email": "test@example.com",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Создаем фиктивный запрос
        request = self.factory.post("/register/", form_data)
        request.session = {}

        # Замещаем функции генерации кода и отправки SMS
        with patch("users.views.generate_verification_code", return_value=str(uuid.uuid4())[:6]) as mock_generate_code:
            with patch("users.views.send_sms") as mock_send_sms:
                # Создаем экземпляр представления и вызываем метод form_valid
                view = UserCreateView()
                view.request = request
                response = view.form_valid(form)

                # Проверяем перенаправление
                self.assertIsInstance(response, HttpResponseRedirect)
                self.assertEqual(response.url, reverse("users:verify-phone"))

                # Проверяем временную сессию
                session = request.session
                self.assertIn("verification_code", session)
                self.assertIn("phone_number", session)
                self.assertIn("email", session)
                self.assertIn("password", session)

                # Проверяем отправку SMS
                mock_send_sms.assert_called_once_with(
                    "+79111111111", f"Ваш код подтверждения: {session['verification_code']}"
                )

                # Генерация кода
                mock_generate_code.assert_called_once()


class PaymentPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(phone_number="+791111111111")

    def test_payment_page_logged_in(self):
        # Логиним пользователя
        self.client.force_login(self.user)

        # Запрашиваем страницу оплаты
        response = self.client.get(reverse("users:payment_page"))

        # Проверяем успешность
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.context)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(phone_number="+791111111111")
        self.client.force_login(self.user)

    def test_logout_view(self):
        # Убедимся, что пользователь изначально авторизован
        self.assertTrue("_auth_user_id" in self.client.session)

        response = self.client.get(reverse("users:logout"))

        self.assertEqual(response.status_code, 302)  # Статус 302 - перенаправление
        self.assertFalse("_auth_user_id" in self.client.session)

        # Проверяем перенаправление на главную страницу
        self.assertRedirects(response, "/")
