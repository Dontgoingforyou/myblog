import threading
from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_share_sends_mail(client, published_post, settings):
    settings.DEFAULT_FROM_EMAIL = 'blog@example.com'
    started = []
    original = threading.Thread

    def capture(*args, **kwargs):
        thread = original(*args, **kwargs)
        started.append(thread)
        return thread

    with patch('blog.views.threading.Thread', capture), patch('blog.views.send_mail') as send_mail:
        response = client.post(
            reverse('blog:post_share', args=[published_post.id]),
            {
                'name': 'Анна',
                'email': 'anna@example.com',
                'to': 'friend@example.com',
                'comments': 'Посмотри',
            },
        )
        for thread in started:
            thread.join(timeout=2)

    assert response.status_code == 200
    assert response.context['sent'] is True
    send_mail.assert_called_once()
    subject, message, sender, recipients = send_mail.call_args.args
    assert published_post.title in subject
    assert 'Посмотри' in message
    assert sender == 'blog@example.com'
    assert recipients == ['friend@example.com']


@pytest.mark.django_db
def test_share_of_draft_returns_404(client, author):
    from blog.models import Post

    draft = Post.objects.create(
        title='Черновик',
        slug='draft',
        author=author,
        body='Скрытый текст',
        status=Post.Status.DRAFT,
    )

    response = client.get(reverse('blog:post_share', args=[draft.id]))

    assert response.status_code == 404
