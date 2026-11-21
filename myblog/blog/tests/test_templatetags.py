import pytest
from django.template import Context, Template


@pytest.mark.parametrize(
    ('number', 'word'),
    [
        (1, 'пост'),
        (2, 'поста'),
        (5, 'постов'),
        (11, 'постов'),
        (21, 'пост'),
    ],
)
def test_russian_pluralize(number, word):
    rendered = Template(
        '{% load blog_extras %}'
        '{{ number|russian_pluralize:"пост,поста,постов" }}'
    ).render(Context({'number': number}))

    assert rendered == word


def test_markdown_renders_list():
    rendered = Template(
        '{% load blog_extras %}{{ text|markdown }}'
    ).render(Context({'text': 'Список:\n\n* Один\n* Два'}))

    assert '<ul>' in rendered
    assert '<li>Один</li>' in rendered


@pytest.mark.django_db
def test_most_commented_ignores_inactive_comments(author):
    from blog.models import Comment, Post
    from blog.templatetags.blog_extras import get_most_commented_posts

    loud = Post.objects.create(
        title='С ответом',
        slug='with-comment',
        author=author,
        body='Текст',
        status=Post.Status.PUBLISHED,
    )
    quiet = Post.objects.create(
        title='Со скрытым',
        slug='hidden-comment',
        author=author,
        body='Текст',
        status=Post.Status.PUBLISHED,
    )
    Comment.objects.create(post=loud, name='Анна', email='anna@example.com', body='Видно', active=True)
    Comment.objects.create(post=quiet, name='Борис', email='boris@example.com', body='Скрыто', active=False)

    ranked = list(get_most_commented_posts(count=2))

    assert ranked[0] == loud


@pytest.mark.django_db
def test_total_posts_counts_only_published(author, published_post):
    from blog.models import Post

    Post.objects.create(
        title='Черновик',
        slug='draft',
        author=author,
        body='Скрытый текст',
        status=Post.Status.DRAFT,
    )
    rendered = Template('{% load blog_extras %}{% total_posts %}').render(Context())

    assert rendered == '1'
