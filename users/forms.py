from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import BooleanField

from posts.models import Subscription
from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs["class"] = "form-check-input"
            else:
                fild.widget.attrs["class"] = "form-control"


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Определяем форму регистрации и проводим валидацию"""

    class Meta:
        model = User
        fields = ("phone_number", "email", "avatar", "country", "password1", "password2")

    def clean_phone_number(self):
        """Проверка уникальности номера, в противном случае уведомление о существовании такого номера."""
        phone_number = self.cleaned_data.get("phone_number")
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Пользователь с данным номером телефона уже зарегистрирован.")
        return phone_number


class VerificationCodeForm(forms.Form):
    """Форма для ввода SMS-кода подтверждения"""

    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"placeholder": "Введите код"}),
        label="Код подтверждения",
    )


class UserProfileForm(StyleFormMixin, forms.ModelForm):
    """Создаем форму с пользователя с заданными полями"""

    class Meta:
        model = User
        fields = ["avatar", "email", "country"]


class SubscriptionForm(forms.ModelForm):
    """Создаем форму поля уровень подписки"""

    class Meta:
        model = Subscription
        fields = ["subscription_level"]
