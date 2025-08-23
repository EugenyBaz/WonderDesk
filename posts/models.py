from django.db import models
from users.models import User


class Series(models.Model):
    title = models.CharField(max_length=255, verbose_name = "Название материала" )
    description = models.TextField(blank=True, verbose_name = "Описание материала")
    cover_image = models.ImageField(upload_to='series_covers/', blank=True, null=True, verbose_name= "Изображение материала")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор" )

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.title


class MediaType(models.TextChoices):
    TEXT = 'TEXT', 'Текстовый пост'
    VIDEO = 'VIDEO', 'Видео'
    IMAGE = 'IMAGE', 'Изображение'


class Post(models.Model):
    series = models.ForeignKey(Series, related_name='posts', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name = "Название поста" )
    description = models.TextField(blank=True, verbose_name = "Описание поста" )
    media_type = models.CharField(max_length=10, choices=MediaType.choices, default=MediaType.TEXT)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True, verbose_name = "Медиафайлы" )  # Загрузка медиафайлов
    content = models.TextField(blank=True, verbose_name = "Текст" )  # Текстовое содержание
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = "Автор" )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name = "Цена" )
    public = models.BooleanField(default=True, verbose_name = "Публикация" )  # Открытый доступ
    premium = models.BooleanField(default=False, verbose_name = "Платный материал" )  # Платный материал
    sequence_order = models.PositiveIntegerField(null=True, blank=True)  # Порядок следования (для серий)
    view_count = models.PositiveIntegerField(default=0, verbose_name = "Счетчик просмотров" )  # Счётчик просмотров
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts', verbose_name = "Лайки" )  # Лайки

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.title


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
        return f"{self.user.username}: {self.text[:50]}"


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions', verbose_name = "Подписчик" )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers', verbose_name = "Автор" )
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        unique_together = ("subscriber", "author")

    def __str__(self):
        return f"{self.subscriber.username} подписался на {self.author.username}"


