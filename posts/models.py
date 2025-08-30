# -*- coding: utf-8 -*-
from datetime import timedelta

from django.db import models
from django.utils.timezone import now

from users.models import User


class MediaType(models.TextChoices):
    VIDEO = 'VIDEO', 'Видео'
    IMAGE = 'IMAGE', 'Изображение'



class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name = "Название поста" )
    description = models.TextField(blank=True, verbose_name = "Содержание поста" )
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True, verbose_name = "Медиафайлы" )  # Загрузка медиафайлов
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор" )
    public = models.BooleanField(default=True, verbose_name = "Публикация" )  # Открытый доступ
    premium = models.BooleanField(default=False, verbose_name = "Платный материал" )  # Платный материал
    view_count = models.PositiveIntegerField(default=0, verbose_name = "Счетчик просмотров" )  # Счётчик просмотров
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts', verbose_name = "Лайки" )  # Лайки

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"{self.user.email}: {self.text[:50]}"


class Subscription(models.Model):
    SUBSCRIPTION_CHOICES = (('SINGLE', 'Разовая подписка'),)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Подписчик")
    subscription_level = models.CharField(max_length=50, choices=SUBSCRIPTION_CHOICES, default='SINGLE', verbose_name="Уровень подписки")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name="Стоимость подписки")
    starts_at = models.DateTimeField(auto_now_add=True, verbose_name= "Дата начала подписки")
    ends_at = models.DateTimeField(null=True, blank=True, verbose_name= "Дата окончания подписки")
    active = models.BooleanField(default=False, verbose_name="Статус активности")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def set_end_date(self):
        """
        Установка конечного срока подписки (+30 дней от начала)
        """
        self.ends_at = self.starts_at + timedelta(days=30)
        self.save()

    def extend_subscription(self):
        """
        Продлить текущую подписку (если есть старая, то продлеваем её срок)
        """
        if self.ends_at:
            new_end_date = self.ends_at + timedelta(days=30)
            self.ends_at = new_end_date
            self.active = True
            self.save()

    def is_valid(self):
        """
        Проверка активности подписки
        """
        now_time = now()
        return self.ends_at > now_time if self.ends_at else False

    def __str__(self):
        return f"{self.user.email} | Подписка до {self.ends_at.strftime('%Y-%m-%d')} | {'Активна' if self.is_valid() else 'Истекла'}"



