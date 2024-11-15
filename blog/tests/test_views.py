from django.test import TestCase
from django.urls import reverse
from blog.models import Post, Comment
from django.contrib.auth import get_user_model
from django.utils import timezone
from taggit.models import Tag

User = get_user_model()


class PostListViewTest(TestCase):
    def setUp(self):
        """ Создание пользователя и пост """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.tag = Tag.objects.create(name='django', slug='django')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )
        self.post.tags.add(self.tag)

    def test_post_list_view(self):
        """ Проверка отображения списка публикации, шаблон, наличие posts в контексте """

        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/list.html')
        self.assertIn('posts', response.context)

    def test_post_list_view_with_tag(self):
        """ Проверка фильтрации публикации по тегу """

        response = self.client.get(reverse('blog:post_list_by_tag', args=[self.tag.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.post, response.context['posts'])


class PostDetailViewTest(TestCase):
    def setUp(self):
        """ Создание пользователя и пост """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_post_detail_view(self):
        """ Проверка отображения публикации """

        url = reverse('blog:post_detail', args=[
            self.post.publish.day,
            self.post.publish.month,
            self.post.publish.year,
            self.post.slug
        ])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/detail.html')
        self.assertEqual(response.context['post'], self.post)


class PostShareViewTest(TestCase):
    def setUp(self):
        """ Создание пользователя и пост """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.tag = Tag.objects.create(name='django', slug='django')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_post_share_view_get(self):
        """ Проверка get-запроса для отображения формы """

        response = self.client.get(reverse("blog:post_share", args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/share.html")

    def test_post_share_view_post(self):
        """ Проверка post-запроса с заполненной формой для отправки письма с проверкой отправки письма """

        response = self.client.post(
            reverse('blog:post_share', args=[self.post.id]),
            data={
                'name': 'Test User',
                'email': 'test@example.com',
                'to': 'test2@example.com',
                'comments': 'test',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['sent'])


class PostCommentViewTest(TestCase):
    def setUp(self):
        """ Создание пользователя и пост """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_post_comment_view_post(self):
        """ Проверка возможности оставлять комментарии через форму, успешное создание комментария для поста """

        response = self.client.post(
            reverse('blog:post_comment', args=[self.post.id]),
            data={
                'name': 'Test User',
                'email': 'test@example.com',
                'body': 'test',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('comment' in response.context)
        self.assertTrue(Comment.objects.filter(post=self.post).exists())


class PostSearchViewTest(TestCase):
    def setUp(self):
        """ Создание пользователя и пост """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_post_search_view(self):
        """ Проверка корректного поиска публикации по запросу """

        response = self.client.get(reverse('blog:post_search'), {'query': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post/search.html')
        self.assertIn(self.post, response.context['results'])