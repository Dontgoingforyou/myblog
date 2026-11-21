import pytest
from django.urls import reverse

from blog.models import Post


@pytest.mark.django_db
def test_empty_search_has_no_results(client):
    response = client.get(reverse('blog:post_search'))

    assert response.status_code == 200
    assert response.context['query'] is None
    assert response.context['results'] == []


@pytest.mark.django_db
def test_search_finds_russian_word_in_body(client, published_post):
    response = client.get(reverse('blog:post_search'), {'query': 'маркдауна'})

    assert list(response.context['results']) == [published_post]


@pytest.mark.django_db
def test_search_second_page_keeps_query(client, author):
    for index in range(11):
        Post.objects.create(
            title=f'Поиск {index}',
            slug=f'search-{index}',
            author=author,
            body='Этот текст тест маркдауна',
            status=Post.Status.PUBLISHED,
        )

    response = client.get(reverse('blog:post_search'), {'query': 'маркдауна', 'page': 2})

    assert response.context['results'].paginator.count == 11
    assert len(list(response.context['results'])) == 1
    html = response.content.decode()
    assert 'page=1' in html
    assert 'query=' in html


@pytest.mark.django_db
def test_search_ignores_unrelated_query(client, published_post):
    response = client.get(reverse('blog:post_search'), {'query': 'кванториум'})

    assert list(response.context['results']) == []
