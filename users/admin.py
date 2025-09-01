from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "email")

    def save_model(self, request, obj, form, change):
        # Если пароль был изменён, хешируем его перед сохранением
        if obj.password:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
