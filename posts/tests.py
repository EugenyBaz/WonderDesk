from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post
from users.models import User


class PostTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(phone_number="+791111111111")
        self.post = Post.objects.create(title="Test Post", description="Пост создан для теста", author=self.user)

        self.client = Client()

    def test_post_retrieve(self):
        url = reverse("posts:post_detail", args=(self.post.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_create(self):
        self.client.force_login(self.user)
        url = reverse("posts:post_create")
        data = {
            "title": "Пост для теста",
            "description": "Пост создан для тестового поля с описанием",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.all().count(), 2)

    def test_post_update(self):
        self.client.force_login(self.user)
        url = reverse("posts:post_update", args=(self.post.pk,))
        data = {"title": "Новый заголовок"}

        response = self.client.post(url, data=data)

        updated_post = Post.objects.get(pk=self.post.pk)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("posts:post_detail", args=(updated_post.pk,)))

        # Проверяем, что пост изменился
        self.assertEqual(updated_post.title, "Новый заголовок")

    def test_post_delete(self):
        self.client.force_login(self.user)
        url = reverse("posts:post_delete", args=(self.post.pk,))

        response = self.client.delete(url)
        self.assertIn(response.status_code, [204, 302])

        remaining_posts = Post.objects.count()
        self.assertEqual(remaining_posts, 0)


class SearchResultsViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(phone_number="+79111111111", email="test@test.ru")
        cls.post1 = Post.objects.create(title="Первый пост", description="Описание первого поста", author=cls.user)
        cls.post2 = Post.objects.create(title="Второй пост", description="Описание второго поста", author=cls.user)

    def test_search_by_title(self):
        """Проверка, что поиск находит совпадающие названия."""
        url = reverse("posts:search_results")
        search_term = "Первый"
        response = self.client.get(f"{url}?q={search_term}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)
        self.assertTemplateUsed(response, "posts/search_results.html")
        self.assertTrue(response.context["results"])
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["query"], search_term)

    def test_search_by_description(self):
        """Проверка, что поиск находит совпадающие описания."""
        url = reverse("posts:search_results")
        search_term = "Описание"
        response = self.client.get(f"{url}?q={search_term}")

        self.assertContains(response, self.post1.description)
        self.assertContains(response, self.post2.description)
        self.assertTemplateUsed(response, "posts/search_results.html")
        self.assertTrue(response.context["results"])
        self.assertEqual(len(response.context["results"]), 2)
        self.assertEqual(response.context["query"], search_term)

    def test_partial_match_search(self):
        """Проверка частичных совпадений при поиске."""
        url = reverse("posts:search_results")
        search_term = "Перв"  # Частичный поиск
        response = self.client.get(f"{url}?q={search_term}")

        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)
        self.assertTemplateUsed(response, "posts/search_results.html")
        self.assertTrue(response.context["results"])
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["query"], search_term)

    def test_no_results_found(self):
        """Проверка поиска без результатов."""
        url = reverse("posts:search_results")
        search_term = "Некоторый случайный текст"
        response = self.client.get(f"{url}?q={search_term}")

        self.assertTemplateUsed(response, "posts/search_results.html")
        self.assertFalse(response.context["results"])  # Никаких результатов найдено
        self.assertEqual(response.context["query"], search_term)
