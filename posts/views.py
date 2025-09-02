from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from posts.forms import PostForm
from posts.models import Post, Subscription
from posts.paginations import CustomPagination


class PostListView(ListView):
    model = Post
    paginate_by = 5  # Количество элементов на странице
    paginator_class = CustomPagination  # Используем кастомный пагинатор

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем список объектов и проходим по ним, создавая расширения
        extensions = {}
        for obj in context["object_list"]:
            if obj.file:
                extensions[obj.id] = obj.file.name.split(".")[-1]
            else:
                extensions[obj.id] = "unknown"  # Значение по умолчанию
        context["extensions"] = extensions
        return context

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True):
        return self.paginator_class(queryset, per_page, orphans, allow_empty_first_page)


class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()
        context["ex"] = obj.file.name.split(".")[-1]
        return context


def contacts(request):
    return render(request, "posts/contacts.html")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Передаем текущего пользователя в форму
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user  # Устанавливаем текущего пользователя как автора
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


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    file_extentions = post.file.name.split(".")[-1]
    print("DEBUG", file_extentions)
    # Бесплатные посты видны всем
    if not post.premium:
        return render(request, "posts:post_detail", {"post": post, "ex": file_extentions})

    # Платные посты видим только подписанным пользователям
    try:
        subscription = Subscription.objects.get(user=request.user)
        if subscription.active:
            return render(request, "posts:post_detail", {"post": post, "ex": file_extentions})
        else:
            return redirect("/subscribe/")
    except Subscription.DoesNotExist:
        return redirect("/subscribe/")


def post_detail_check(request, pk):
    post = get_object_or_404(Post, pk=pk)
    file_extentions = post.file.name.split(".")[-1]
    file_contents = ""
    if post.file:
        file_contents = mark_safe(post.file.read())
    return render(request, "posts:post_detail", {"post": post, "file_contents": file_contents, "ex": file_extentions})


class SearchResultsView(TemplateView):
    template_name = "posts/search_results.html"

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")  # Получаем запрос и очищаем пробелы

        if query:
            # Производим поиск по названию и описанию
            results = Post.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        else:
            # Если запрос пустой, возвращаем пустую коллекцию
            results = Post.objects.none()

        context = {
            "results": results,
            "query": query,
            "user": request.user,  # Добавляем текущего пользователя
        }

        return render(request, self.template_name, context)
