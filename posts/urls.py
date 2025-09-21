from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from posts.apps import PostsConfig
from posts.views import (PostCreateView, PostDeleteView, PostDetailView, PostListView, PostUpdateView,
                         SearchResultsView, contacts)

app_name = PostsConfig.name


urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("contacts/", contacts, name="contacts"),
    path("post/<int:pk>/", (PostDetailView.as_view()), name="post_detail"),
    path("create_post/", PostCreateView.as_view(), name="post_create"),
    path("<int:pk>/update/", PostUpdateView.as_view(), name="post_update"),
    path("<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("search/", SearchResultsView.as_view(), name="search_results"),
]  # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
