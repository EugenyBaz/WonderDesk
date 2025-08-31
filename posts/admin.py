from django.contrib import admin

from posts.models import Post, Subscription


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description")
    search_fields = ("title", "description", "author")


@admin.register(Subscription)
class Subscription(admin.ModelAdmin):
    list_display = ("id", "subscription_level", "price", "starts_at", "ends_at", "active")
    search_fields = ("id", "subscription_level", "price")
