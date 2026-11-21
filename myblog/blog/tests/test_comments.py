import pytest
from django.urls import reverse

from blog.models import Comment


@pytest.mark.django_db
def test_comment_is_saved(client, published_post):
    response = client.post(
        reverse('blog:post_comment', args=[published_post.id]),
        {'name': 'Анна', 'email': 'anna@example.com', 'body': 'Привет'},
    )

    assert response.status_code == 200
    comment = Comment.objects.get()
    assert comment.post == published_post
    assert comment.body == 'Привет'
    assert comment.active is True


@pytest.mark.django_db
def test_invalid_comment_is_not_saved(client, published_post):
    response = client.post(
        reverse('blog:post_comment', args=[published_post.id]),
        {'name': 'Анна', 'email': 'не-почта', 'body': 'Привет'},
    )

    assert response.status_code == 200
    assert response.context['comment'] is None
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_comment_get_is_not_allowed(client, published_post):
    response = client.get(reverse('blog:post_comment', args=[published_post.id]))

    assert response.status_code == 405
