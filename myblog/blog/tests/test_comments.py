import logging

import pytest
from django.urls import reverse

from blog.models import Comment, Post


def comment_payload(client, data):
    session = client.session
    token = session.get('comment_token') or 'test-token'
    session['comment_token'] = token
    session.save()
    payload = dict(data)
    payload['token'] = token
    return payload


@pytest.mark.django_db
def test_comment_is_saved(client, published_post, caplog):
    caplog.set_level(logging.INFO, logger='blog.views')
    response = client.post(
        reverse('blog:post_comment', args=[published_post.id]),
        comment_payload(client, {'name': 'Анна', 'email': 'anna@example.com', 'body': 'Привет'}),
    )

    assert response.status_code == 302
    comment = Comment.objects.get()
    assert response.url == f'{published_post.get_absolute_url()}#comment-{comment.id}'
    page = client.get(published_post.get_absolute_url())
    content = page.content.decode()
    assert 'Комментарий добавлен.' in content
    assert 'value="Анна"' in content
    assert 'value="anna@example.com"' in content
    assert comment.post == published_post
    assert comment.body == 'Привет'
    assert comment.active is True
    assert f'Комментарий {comment.id} к посту {published_post.id}' in caplog.text
    assert 'anna@example.com' not in caplog.text


@pytest.mark.django_db
def test_invalid_comment_is_not_saved(client, published_post):
    response = client.post(
        reverse('blog:post_comment', args=[published_post.id]),
        comment_payload(client, {'name': 'Анна', 'email': 'не-почта', 'body': 'Привет'}),
    )

    assert response.status_code == 200
    assert 'Не удалось отправить комментарий' in response.content.decode()
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_reply_is_saved_under_comment(client, published_post):
    parent = Comment.objects.create(
        post=published_post,
        name='Анна',
        email='anna@example.com',
        body='Первый',
    )

    response = client.post(
        reverse('blog:post_comment', args=[published_post.id]),
        comment_payload(client, {
            'name': 'Борис',
            'email': 'boris@example.com',
            'body': 'Ответ Анне',
            'parent': parent.id,
        }),
    )

    reply = Comment.objects.get(body='Ответ Анне')
    assert response.status_code == 302
    page = client.get(published_post.get_absolute_url())
    assert 'Ответ добавлен.' in page.content.decode()
    assert reply.parent == parent
    assert reply.post == published_post


@pytest.mark.django_db
def test_reply_to_other_post_is_not_attached(client, author, published_post):
    other = Post.objects.create(
        title='Другой',
        slug='other',
        author=author,
        body='Текст',
        status=Post.Status.PUBLISHED,
    )
    foreign = Comment.objects.create(
        post=other,
        name='Анна',
        email='anna@example.com',
        body='Чужой',
    )

    response = client.post(
        reverse('blog:post_comment', args=[published_post.id]),
        {'name': 'Борис', 'email': 'boris@example.com', 'body': 'Ответ', 'parent': foreign.id},
    )

    assert response.status_code == 404
    assert Comment.objects.filter(body='Ответ').exists() is False


@pytest.mark.django_db
def test_detail_nests_reply_under_comment(client, published_post):
    parent = Comment.objects.create(
        post=published_post,
        name='Анна',
        email='anna@example.com',
        body='Первый',
    )
    Comment.objects.create(
        post=published_post,
        parent=parent,
        name='Борис',
        email='boris@example.com',
        body='Ответ Анне',
    )

    response = client.get(published_post.get_absolute_url())
    content = response.content.decode()
    thread = response.context['comments']

    assert response.context['comments_count'] == 2
    assert [comment.body for comment in thread] == ['Первый']
    assert [reply.body for reply in thread[0].thread_replies] == ['Ответ Анне']
    assert 'Ответить Анна' in content
    assert 'Ответить Борис' in content


@pytest.mark.django_db
def test_repeated_comment_is_not_saved(client, published_post):
    url = reverse('blog:post_comment', args=[published_post.id])
    payload = comment_payload(client, {'name': 'Анна', 'email': 'anna@example.com', 'body': 'Привет'})

    first = client.post(url, payload)
    second = client.post(url, payload)

    assert first.status_code == 302
    assert second.status_code == 302
    assert Comment.objects.count() == 1
    page = client.get(published_post.get_absolute_url())
    assert 'Комментарий уже отправлен.' in page.content.decode()


@pytest.mark.django_db
def test_reply_to_inactive_comment_stays_hidden(client, published_post):
    parent = Comment.objects.create(
        post=published_post,
        name='Анна',
        email='anna@example.com',
        body='Скрытый',
        active=False,
    )
    Comment.objects.create(
        post=published_post,
        parent=parent,
        name='Борис',
        email='boris@example.com',
        body='Ответ на скрытый',
    )

    response = client.get(published_post.get_absolute_url())

    assert response.context['comments'] == []
    assert response.context['comments_count'] == 0
    assert 'Ответ на скрытый' not in response.content.decode()


@pytest.mark.django_db
def test_comments_are_paginated(client, published_post):
    first = None
    for index in range(11):
        comment = Comment.objects.create(
            post=published_post,
            name='Анна',
            email='anna@example.com',
            body=f'Корень {index:02d}',
        )
        if first is None:
            first = comment
    Comment.objects.create(
        post=published_post,
        parent=first,
        name='Борис',
        email='boris@example.com',
        body='Ответ на первый',
    )

    page = client.get(published_post.get_absolute_url(), {'page': 2})

    assert page.context['comments_count'] == 12
    assert [comment.body for comment in page.context['comments']] == ['Корень 10']
    assert 'Ответ на первый' not in page.content.decode()
    assert 'page=1' in page.content.decode()


@pytest.mark.django_db
def test_comment_get_is_not_allowed(client, published_post):
    response = client.get(reverse('blog:post_comment', args=[published_post.id]))

    assert response.status_code == 405
