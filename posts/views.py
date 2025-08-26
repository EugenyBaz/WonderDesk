from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from posts.paginations import CustomPagination
from posts.service import get_post_by_chapter
from django.core.cache import cache

from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden

from posts.forms import PostForm
from posts.models import Post, Chapter, Subscription


class PostListView(ListView):
    model = Post
    paginate_by = 3  # Количество элементов на странице
    paginator_class = CustomPagination  # Используем кастомный пагинатор

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return self.paginator_class(queryset, per_page, orphans, allow_empty_first_page)


class PostDetailView(DetailView):
    model = Post


def contacts(request):
    return render(request, "posts/contacts.html")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        post = form.save()
        user = self.request.user
        post.author = user
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})  # Передаем пользователя в форму
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            "posts:post_detail",
            kwargs={
                "pk": self.object.pk,
            },
        )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("posts:home")

    def test_func(self):
        obj = self.get_object()
        return self.request.user.has_perm("posts.can_delete_any_post") or obj.author == self.request.user

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет права удалять продукт.")


class UnpublishPostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ["public"]
    template_name_suffix = "_unpublish"

    def test_func(self):
        obj = self.get_object()
        return self.request.user.has_perm("catalog.can_unpublish_post") or obj.author == self.request.user

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет права отменять публикацию продукта.")

    def form_valid(self, form):
        form.instance.publication = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})


class PostByChapterView(ListView):
    model = Post
    template_name = "posts/posts_by_chapter.html"  # отдельный шаблон для вывода постов по главам

    def get_queryset(self):
        chapter_id = self.kwargs.get("chapter_id")
        return get_post_by_chapter(chapter_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter_id = self.kwargs.get("chapter_id")
        context["current_chapter"] = Chapter.objects.get(pk=chapter_id)
        return context


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # Бесплатные посты видны всем
    if not post.premium:
        return render(request, "posts:post_detail", {'post': post})

    # Платные посты видим только подписанным пользователям
    try:
        subscription = Subscription.objects.get(user=request.user)
        if subscription.active:
            return render(request, "posts:post_detail", {'post': post})
        else:
            return redirect('/subscribe/')
    except Subscription.DoesNotExist:
        return redirect('/subscribe/')

def post_detail_check(request, pk):
    post = get_object_or_404(Post, pk=pk)
    file_contents = ""
    if post.file:
        file_contents = mark_safe(post.file.read())
    return render(request, "posts:post_detail", {'post': post, 'file_contents': file_contents})
