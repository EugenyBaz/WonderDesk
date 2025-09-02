from django.core.exceptions import ValidationError
from django.forms import BooleanField, ModelForm

from posts.constants import FORBIDDEN_WORDS
from posts.models import Post

forbidden_list = FORBIDDEN_WORDS


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class PostForm(StyleFormMixin, ModelForm):

    class Meta:
        model = Post
        fields = ["title", "description", "file", "premium"]
        exclude = ("author", "public", "sequence_order", "view_count", "likes")  # Скрываем ненужные поля

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")

        if instance is not None and not (
            self.user.has_perm("posts.can_unpublish_post") or instance.author == self.user
        ):
            self.Meta.exclude = ("public",)  # Исключаем поле "public"
        else:
            self.Meta.fields = "__all__"

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.author = self.user  # Устанавливаем текущего пользователя автором
        obj.public = True  # Публикуем запись автоматически
        if commit:
            obj.save()
        return obj

    def clean_title(self):

        cleaned_data = super().clean()
        name = cleaned_data.get("title").strip().lower()
        words_in_name = name.split()

        for word in words_in_name:
            if word in FORBIDDEN_WORDS:
                raise ValidationError(f"Введено  недопустимое  слово '{word}'.")
        return cleaned_data.get("title")

    def clean_description(self):

        cleaned_data = super().clean()
        description = cleaned_data.get("description").strip().lower()
        words_in_description = description.split()

        for word in words_in_description:
            if word in forbidden_list:
                raise ValidationError(f"Введено  недопустимое  слово '{word}'.")
        return cleaned_data.get("description")

    def clean_price(self):

        cleaned_data = super().clean()
        data = cleaned_data.get("price")
        price = float(data)

        if price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
        return price
