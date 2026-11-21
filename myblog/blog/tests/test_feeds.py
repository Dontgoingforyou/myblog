import pytest
from django.urls import reverse

from blog.models import Post


@pytest.mark.django_db
def test_feed_contains_published_post(client, published_post):
    response = client.get(reverse('blog:post_feed'))

    assert response.status_code == 200
    assert published_post.title in response.content.decode()


@pytest.mark.django_db
def test_feed_hides_draft(client, author):
    Post.objects.create(
        title='Черновик ленты',
        slug='draft-feed',
        author=author,
        body='Скрытый текст',
        status=Post.Status.DRAFT,
    )

    response = client.get(reverse('blog:post_feed'))

    assert 'Черновик ленты' not in response.content.decode()


@pytest.mark.django_db
def test_sitemap_contains_published_post(client, published_post):
    response = client.get(reverse('django.contrib.sitemaps.views.sitemap'))

    assert response.status_code == 200
    assert published_post.get_absolute_url() in response.content.decode()
