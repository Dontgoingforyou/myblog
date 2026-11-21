import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from blog.models import Post


@pytest.mark.django_db
def test_seed_fills_empty_blog_once():
    call_command('seed')

    assert Post.published.count() == 4
    assert Post.objects.filter(status=Post.Status.DRAFT, slug='chernovik').exists()
    author = get_user_model().objects.get(username='author')
    assert author.has_usable_password() is False
    commented = Post.objects.get(slug='kommentarii')
    assert commented.comments.filter(parent__isnull=True).count() == 1
    assert commented.comments.filter(parent__isnull=False).count() == 1
    assert Post.objects.get(slug='poisk-po-slovu').cover

    call_command('seed')

    assert Post.objects.count() == 5


@pytest.mark.django_db
def test_seed_keeps_existing_posts(author):
    Post.objects.create(
        title='Свой пост',
        slug='svoi-post',
        author=author,
        body='Текст',
        status=Post.Status.PUBLISHED,
    )

    call_command('seed')

    assert Post.objects.filter(slug='svoi-post').exists()
    assert Post.objects.filter(slug='poisk-po-slovu').count() == 1
