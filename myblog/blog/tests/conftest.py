import pytest
from django.contrib.auth import get_user_model

from blog.models import Post


@pytest.fixture
def author(db):
    return get_user_model().objects.create_user(username='author', password='pass')


@pytest.fixture
def published_post(author):
    post = Post.objects.create(
        title='Тест markdown',
        slug='test-markdown',
        author=author,
        body='Этот текст тест маркдауна',
        status=Post.Status.PUBLISHED,
    )
    post.tags.add('python')
    return post
