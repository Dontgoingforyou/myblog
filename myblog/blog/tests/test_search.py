import pytest
from django.urls import reverse


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
def test_search_ignores_unrelated_query(client, published_post):
    response = client.get(reverse('blog:post_search'), {'query': 'кванториум'})

    assert list(response.context['results']) == []
