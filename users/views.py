from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.forms import UserRegisterForm, VerificationCodeForm
from users.models import User
from users.serializers import UserSerializer
from users.utils import generate_verification_code, send_sms


class UserCreateView(SuccessMessageMixin,CreateView):
    """ Представление для регистрации пользователя"""
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy("users:verify-phone")
    success_message = "Вы успешно начали регистрацию. Проверьте телефон для подтверждения."


    def form_valid(self, form):
        # Создаем пользователя, но пока не активируем его
        phone_number = form.cleaned_data['phone_number']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']

        # Генерируем код подтверждения и отправляем SMS
        verification_code = generate_verification_code()
        send_sms(phone_number, f"Ваш код подтверждения: {verification_code}")

        # Временное хранение кода в сессии
        self.request.session['verification_code'] = verification_code
        self.request.session['phone_number'] = phone_number
        self.request.session['email'] = email
        self.request.session['password'] = password

        # return super().form_valid(form)

        return redirect("users:verify-phone")

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        data = serializer.validated_data
        password = data.pop("password")
        user = serializer.save(is_active=True)
        user.set_password(password)
        user.save()

        # Генерируем JWT-токены
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(tokens, status=status.HTTP_201_CREATED)


def verify_phone(request):
    if request.method == 'POST':
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['code']
            expected_code = request.session.get('verification_code')
            if entered_code == expected_code:
                phone_number = request.session.get('phone_number')
                email = request.session.get('email')
                password = request.session.get('password')

                user = User.objects.create_user(
                    phone_number=phone_number,
                    email=email,
                    password= password,
                    is_active=True
                )

                # Удаляем код из сессии
                del request.session['verification_code']
                del request.session['phone_number']
                del request.session['email']
                del request.session['password']

                messages.success(request, "Регистрация успешно завершена!")
                return redirect('users:login')
            else:
                form.add_error(None, "Неверный код подтверждения")
    else:
        form = VerificationCodeForm()

    return render(request, 'users/verify_phone.html', {'form': form})

