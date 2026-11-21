from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from blog.models import Comment, Post


@pytest.mark.django_db
def test_list_shows_only_published_posts(client, author, published_post):
    draft = Post.objects.create(
        title='Черновик',
        slug='draft',
        author=author,
        body='Скрытый текст',
        status=Post.Status.DRAFT,
    )

    response = client.get(reverse('blog:post_list'))

    assert response.status_code == 200
    titles = [post.title for post in response.context['posts']]
    assert published_post.title in titles
    assert draft.title not in titles


@pytest.mark.django_db
def test_list_second_page_has_one_post(client, author):
    now = timezone.now()
    for index in range(4):
        Post.objects.create(
            title=f'Пост {index}',
            slug=f'post-{index}',
            author=author,
            body='Текст',
            status=Post.Status.PUBLISHED,
            publish=now - timedelta(days=index),
        )

    response = client.get(reverse('blog:post_list'), {'page': 2})

    assert response.status_code == 200
    assert [post.title for post in response.context['posts']] == ['Пост 3']


@pytest.mark.django_db
def test_tag_page_filters_posts(client, author, published_post):
    other = Post.objects.create(
        title='Без тега',
        slug='no-tag',
        author=author,
        body='Текст',
        status=Post.Status.PUBLISHED,
    )

    response = client.get(reverse('blog:post_list_by_tag', args=['python']))

    titles = [post.title for post in response.context['posts']]
    assert titles == [published_post.title]
    assert other.title not in titles


@pytest.mark.django_db
def test_unknown_tag_returns_404(client):
    response = client.get(reverse('blog:post_list_by_tag', args=['missing']))

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_returns_published_post(client, published_post):
    response = client.get(published_post.get_absolute_url())

    assert response.status_code == 200
    assert response.context['post'] == published_post


@pytest.mark.django_db
def test_detail_hides_draft(client, author):
    draft = Post.objects.create(
        title='Черновик',
        slug='draft',
        author=author,
        body='Скрытый текст',
        status=Post.Status.DRAFT,
    )

    response = client.get(draft.get_absolute_url())

    assert response.status_code == 404


@pytest.mark.django_db
def test_detail_lists_similar_post_with_shared_tag(client, author, published_post):
    similar = Post.objects.create(
        title='Похожий пост',
        slug='similar',
        author=author,
        body='Текст',
        status=Post.Status.PUBLISHED,
    )
    similar.tags.add('python')

    response = client.get(published_post.get_absolute_url())

    assert list(response.context['similar_posts']) == [similar]


@pytest.mark.django_db
def test_detail_hides_inactive_comment(client, published_post):
    Comment.objects.create(
        post=published_post,
        name='Анна',
        email='anna@example.com',
        body='Скрытый комментарий',
        active=False,
    )

    response = client.get(published_post.get_absolute_url())

    assert list(response.context['comments']) == []
