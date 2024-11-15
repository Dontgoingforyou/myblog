from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from blog.models import Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ Создаем пользователя для автора поста и два поста, один черновик, второй опубликован """
        cls.user = User.objects.create_user(username='testuser', password='password')

        cls.draft_post = Post.objects.create(
            title='Draft post',
            slug='draft-post',
            author=cls.user,
            body='Это черновик поста',
            publish=timezone.now(),
            status=Post.Status.DRAFT
        )
        cls.published_post = Post.objects.create(
            title='Published post',
            slug='published-post',
            author=cls.user,
            body='Это опубликованный пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )

    def test_post_str(self):
        """ Проверка метода __str__ """

        self.assertEqual(str(self.draft_post), 'Draft post')
        self.assertEqual(str(self.published_post), 'Published post')

    def test_get_absolute_url(self):
        """ Проверка метода get_absolute_url, возвращает ожидаемый URL """

        expected_url = (f'/{self.published_post.publish.day}/{self.published_post.publish.month}/'
                        f'{self.published_post.publish.year}/{self.published_post.slug}/')
        self.assertEqual(self.published_post.get_absolute_url(), expected_url)

    def test_published_manager(self):
        """ Проверка PublishedManager, он должен возвращать только опубликованный пост """

        published_posts = Post.published.all()
        self.assertIn(self.published_post, published_posts)
        self.assertNotIn(self.draft_post, published_posts)

    def test_default_ordering(self):
        """ Проверка сортировки постов по полю publish по убыванию """

        posts = Post.objects.all()
        self.assertEqual(posts[0], self.published_post)


class CommentModelPost(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ Создание пользователя и пост для комментария """
        cls.user = User.objects.create_user(username='testuser', password='password')

        cls.post = Post.objects.create(
            title='Test post',
            slug='test-post',
            author=cls.user,
            body='Это тестовый пост',
            publish=timezone.now(),
            status=Post.Status.PUBLISHED
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            name='Commenter',
            email='commenter@example.com',
            body='Это тестовый комментарий',
            active=True
        )

    def test_comment_str(self):
        """ Проверка метода __str__ """

        self.assertEqual(str(self.comment), f'Комментарий от Commenter к {self.post}')

    def test_comment_post_relationship(self):
        """ Проверка привязки комментария к посту """

        self.assertEqual(self.comment.post, self.post)

    def test_comment_ordering(self):
        """ Проверка сортировки комментариев по полю created по возрастанию """

        comments = Comment.objects.all()
        self.assertEqual(comments[0], self.comment)
