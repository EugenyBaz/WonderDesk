from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import BaseUserManager

from config import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Поле Номер телефона обязательно!")

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(phone_number=phone_number, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    """Модель пользователя с регистрацией по телефону"""
    username = None
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар")
    phone_number = models.CharField(unique=True, max_length=50, verbose_name="Телефон", help_text="Введите номер телефона")
    country = models.CharField(max_length=50,blank=True, null=True, verbose_name="Страна")
    token = models.CharField(max_length=100, verbose_name="Токен", blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.phone_number

PAYMENT_METHODS = (("cash", "Наличные"), ("transfer", "Перевод на счёт"))

class Payment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    payment_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата платежа"
    )
    paid_chapter = models.ForeignKey(
        "posts.Chapter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс/блок",
    )
    paid_post = models.ForeignKey(
        "posts.Post",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Отдельно оплаченный пост",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        default="cash",
        verbose_name="Способ оплаты",
    )
    stripe_payment_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="ID платежа в Stripe"
    )
    link_payment = models.URLField(
        max_length=400, verbose_name="Ссылка на оплату", blank=True, null=True
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платёж {self.user.email}, {self.payment_date}"

