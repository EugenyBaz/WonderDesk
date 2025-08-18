from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Модель пользователя с регистрацией по телефону"""
    username = None
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар")
    phone_number = models.CharField(unique=True, max_length=50, verbose_name="Телефон", help_text="Введите номер телефона")
    country = models.CharField(max_length=50,blank=True, null=True, verbose_name="Страна")
    token = models.CharField(max_length=100, verbose_name="Токен", blank=True, null=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.phone_number

