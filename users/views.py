

from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin

from users.forms import UserRegisterForm
from users.models import User
from users.utils import generate_verification_code, send_sms



class UserCreateView(SuccessMessageMixin,CreateView):
    """ Представление для регистрации пользователя"""
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy("users:login")
    success_message = "Вы успешно зарегистрировались!"


    def form_valid(self, form):
        # Создаем пользователя, но пока не активируем его
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # Генерируем код подтверждения и отправляем SMS
        verification_code = generate_verification_code()
        send_sms(user.phone_number, f"Ваш код подтверждения: {verification_code}")

        # Временное хранение кода в сессии
        self.request.session['verification_code'] = verification_code

        return super().form_valid(form)