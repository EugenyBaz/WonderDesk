from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin

from users.forms import UserRegisterForm, VerificationCodeForm
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
        self.request.session['phone_number'] = user.phone_number

        return super().form_valid(form)



def verify_phone(request):
    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            expected_code = request.session.get('verification_code')
            if entered_code == expected_code:
                # Код подтвержден, активируем пользователя
                user = User.objects.get(phone_number=request.session.get('phone_number'))
                user.is_active = True
                user.save()

                # Удаляем код из сессии
                del request.session['verification_code']
                del request.session['phone_number']

                messages.success(request, "Регистрация успешно завершена!")
                return redirect('users:login')
            else:
                form.add_error(None, "Неверный код подтверждения")
    else:
        form = VerificationCodeForm()

    return render(request, 'users/verify_phone.html', {'form': form})