from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from django.test import TestCase
from django.utils import timezone

from blog.models import Post
from blog.views import post_list, post_detail, post_comment, post_search

User = get_user_model()


class BlogUrlsTest(TestCase):
    def test_post_list_url(self):
        """ Проверка URL для страницы списка постов """

        url = reverse('blog:post_list')
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(url, '/')
        self.assertEqual(resolve(url).func, post_list)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/list.html")

    def test_post_detail_url(self):
        """ Проверка URL для страницы детального просмотра поста """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )
        url = reverse('blog:post_detail', args=[
            self.post.publish.day, self.post.publish.month, self.post.publish.year, self.post.slug
        ])
        response = self.client.get(url)
        self.assertEqual(url, f'/{self.post.publish.day}/{self.post.publish.month}/{self.post.publish.year}'
                              f'/{self.post.slug}/')
        self.assertEqual(resolve(url).func, post_detail)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/detail.html")
        self.assertEqual(response.context['post'], self.post)

    def test_post_comment_url(self):
        """ Проверка URL для страницы комментариев """

        self.user = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=self.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )
        url = reverse('blog:post_comment', args=[self.post.id])
        response = self.client.post(url, data={
            'body': 'test',
            'name': 'Test Commenter',
            'email': 'test@example.com'
        })
        self.assertEqual(url, f'/{self.post.id}/comment/')
        self.assertEqual(resolve(url).func, post_comment)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/comment.html")
        self.assertEqual(self.post.comments.count(), 1)
        comment = self.post.comments.first()
        self.assertEqual(comment.body, 'test')
        self.assertEqual(response.context['comment'], comment)

    def test_post_search_url(self):
        """ Проверка URL для страницы поиска постов """

        url = reverse('blog:post_search')
        response = self.client.get(reverse("blog:post_search"))
        self.assertEqual(url, '/search/')
        self.assertEqual(resolve(url).func, post_search)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post/search.html")