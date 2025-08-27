from django.contrib import admin
from posts.models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "description" )
    search_fields = ("title", "description", "author" )

