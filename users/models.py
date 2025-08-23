from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import BaseUserManager


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

