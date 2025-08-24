from django.contrib import admin
from posts.models import Chapter, Post


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title", "description", "author")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "description" )
    list_filter = ("series",)
    search_fields = ("name", "description", "author" )


