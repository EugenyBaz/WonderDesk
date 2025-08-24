from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.decorators.cache import cache_page

from posts.apps import PostsConfig
from posts.views import PostListView, contacts, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView

app_name = PostsConfig.name


urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("contacts/", contacts, name="contacts"),
    path("post/<int:pk>/", cache_page(60)(PostDetailView.as_view()), name="post_detail"),
    path("create_post/", PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/update/", PostUpdateView.as_view(), name="post_update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    # path("post/chapter/<slug:chapter_slug>/", PostListView.as_view(), name="product_list_by_category"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)