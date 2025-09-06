import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from posts.models import Subscription
from users.forms import SubscriptionForm, UserProfileForm, UserRegisterForm, VerificationCodeForm
from users.models import Payment, User
from users.serializers import PaymentSerializer, UserSerializer
from users.services import create_stripe_price, create_stripe_product, create_stripe_session
from users.utils import generate_verification_code, send_sms

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class UserCreateView(SuccessMessageMixin, CreateView):
    """Представление для регистрации пользователя"""

    model = User
    form_class = UserRegisterForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:verify-phone")
    success_message = "Вы успешно начали регистрацию. Проверьте телефон для подтверждения."

    def form_valid(self, form):
        # Создаем пользователя, но пока не активируем его
        phone_number = form.cleaned_data["phone_number"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]

        # Генерируем код подтверждения и отправляем SMS
        verification_code = generate_verification_code()
        send_sms(phone_number, f"Ваш код подтверждения: {verification_code}")

        # Временное хранение кода в сессии
        self.request.session["verification_code"] = verification_code
        self.request.session["phone_number"] = phone_number
        self.request.session["email"] = email
        self.request.session["password"] = password

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
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(tokens, status=status.HTTP_201_CREATED)


def payment_page(request):
    if request.user.is_authenticated:
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        context = {
            "access_token": access_token,
        }
        return render(request, "posts/post_detail.html", context)


def verify_phone(request):
    if request.method == "POST":
        form = VerificationCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data["code"]
            expected_code = request.session.get("verification_code")
            if entered_code == expected_code:
                phone_number = request.session.get("phone_number")
                email = request.session.get("email")
                password = request.session.get("password")

                User.objects.create_user(phone_number=phone_number, email=email, password=password, is_active=True)

                # Удаляем код из сессии
                del request.session["verification_code"]
                del request.session["phone_number"]
                del request.session["email"]
                del request.session["password"]

                messages.success(request, "Регистрация успешно завершена!")
                return redirect("users:login")
            else:
                form.add_error(None, "Неверный код подтверждения")
    else:
        form = VerificationCodeForm()

    return render(request, "users/verify_phone.html", {"form": form})


class CustomLogoutView(BaseLogoutView):
    def dispatch(self, request, *args, **kwargs):
        # Обеспечиваем полный выход пользователя
        logout(request)

        response = super().dispatch(request, *args, **kwargs)
        response.delete_cookie(settings.SESSION_COOKIE_NAME)

        # Перенаправляем пользователя на главную страницу
        return HttpResponseRedirect("/")


class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["paid_post", "method"]
    ordering_fields = ["payment_date"]


@login_required
def payment_api_view(request):
    if request.method == "POST":

        try:
            subscription = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:

            subscription = Subscription.objects.create(
                user=request.user, subscription_level="SINGLE", price=100.00  # или любая другая сумма
            )
            subscription.set_end_date()  # Устанавливаем конец подписки
            subscription.save()

            # return render(request, 'users/error.html', {"message": "Подписка не найдена"})

        # Создаем продукт и цену в Stripe
        post_id = create_stripe_product(subscription.subscription_level)
        amount_in_rub = subscription.price
        price = create_stripe_price(post_id, amount_in_rub)
        session_id, payment_link = create_stripe_session(price)

        # Создаем запись о платеже
        Payment.objects.create(
            user=request.user,
            paid_subscription=subscription,
            amount=amount_in_rub,
            method="transfer",
            stripe_payment_id=session_id,
            link_payment=payment_link,
        )

        subscription.active = True
        subscription.save()

        # Выполняем редирект на страницу оплаты
        return redirect(payment_link)

    return render(request, "posts/post_detail.html")


@login_required
def payment_success(request):
    session_id = request.GET.get("session_id")
    try:
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        current_user = request.user
        if checkout_session.payment_status == "paid":
            current_user.subscription_status = True
            current_user.save()
            messages.success(request, "Оплата успешно произведена!")
        else:
            messages.warning(request, "Платеж пока не подтвержден.")

        # Предполагаем, что идентификатор поста сохранён в метаданных Stripe-сессии
        post_pk = checkout_session.metadata.get("post_id")
        return redirect("posts:post_detail", pk=post_pk)

    except Exception as e:
        messages.error(request, f"Ошибка обработки платежа: {e}")
        return redirect("posts:post_detail")


logger = logging.getLogger(__name__)


class CabinetView(LoginRequiredMixin, FormView):
    template_name = "users/cabinet.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("users:cabinet")

    def get_initial(self):
        initial = super().get_initial()
        initial["email"] = self.request.user.email
        initial["country"] = self.request.user.country

        # Попробуем получить подписку пользователя
        subscription = Subscription.objects.filter(user=self.request.user).first()
        if subscription:
            initial["subscription_level"] = subscription.subscription_level

        return initial

    def get_context_data(self, **kwargs):
        """Перезаписываем стандартный метод для передачи контекста."""
        context = super().get_context_data(**kwargs)
        context["has_subscription"] = (
            hasattr(self.request.user, "subscriptions") and self.request.user.subscriptions.exists()
        )

        if context["has_subscription"]:
            context["subscription_form"] = SubscriptionForm()

        return context

    def form_valid(self, form):
        user = self.request.user
        user.email = form.cleaned_data["email"]
        user.country = form.cleaned_data["country"]
        user.save()

        # Сначала смотрим, есть ли подписка
        try:
            subscription = Subscription.objects.get(user=user)
        except Subscription.DoesNotExist:
            # Если подписки нет, мы её не пытаемся обновить
            return super().form_valid(form)

        # Если подписка есть, обновляем её уровень
        subscription.subscription_level = form.cleaned_data.get("subscription_level", "SINGLE")
        subscription.save()

        return super().form_valid(form)
