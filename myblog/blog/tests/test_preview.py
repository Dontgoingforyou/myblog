from io import BytesIO

import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from blog.models import PostImage


def png_file(name):
    buffer = BytesIO()
    Image.new('RGB', (8, 8), 'red').save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@pytest.mark.django_db
def test_detail_describes_post_for_link_preview(client, published_post):
    published_post.summary = 'Короткое описание поста'
    published_post.save(update_fields=['summary'])

    response = client.get(published_post.get_absolute_url())
    content = response.content.decode()

    assert response.status_code == 200
    assert '<meta property="og:title" content="Тест markdown">' in content
    assert '<meta property="og:description" content="Короткое описание поста">' in content
    assert '<meta property="og:type" content="article">' in content
    assert 'og:image' not in content


@pytest.mark.django_db
def test_detail_uses_body_when_summary_is_empty(client, published_post):
    response = client.get(published_post.get_absolute_url())

    assert 'content="Этот текст тест маркдауна"' in response.content.decode()


@pytest.mark.django_db
def test_cover_is_shown_and_used_in_preview(client, published_post):
    published_post.cover = png_file('cover.png')
    published_post.save()

    response = client.get(published_post.get_absolute_url())
    content = response.content.decode()
    cover_url = published_post.cover.url

    assert f'src="{cover_url}"' in content
    assert f'<meta property="og:image" content="http://testserver{cover_url}">' in content

    list_response = client.get('/blog/')
    assert f'src="{cover_url}"' in list_response.content.decode()


@pytest.mark.django_db
def test_markdown_image_from_upload_is_rendered(client, published_post):
    image = PostImage.objects.create(post=published_post, image=png_file('inside.png'))
    published_post.body = f'Абзац\n\n![]({image.image.url})'
    published_post.save(update_fields=['body'])

    response = client.get(published_post.get_absolute_url())

    assert f'<img alt="" src="{image.image.url}"' in response.content.decode()
