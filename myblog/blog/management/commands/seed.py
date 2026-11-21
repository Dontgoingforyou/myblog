from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Comment, Post


def _at(year, month, day):
    return timezone.make_aware(datetime(year, month, day, 12, 0))


POSTS = [
    {
        'title': 'Поиск по слову, а не по всей строке',
        'slug': 'poisk-po-slovu',
        'publish': _at(2026, 11, 2),
        'tags': ['поиск', 'postgresql'],
        'body': (
            'Триграммы по всей фразе почти не находят короткое русское слово внутри длинного заголовка.\n\n'
            'Сравнение идёт с отдельными словами заголовка и текста. Порог — 0.4.\n\n'
            'Искать здесь можно слово «триграммы».'
        ),
    },
    {
        'title': 'Пустая строка перед списком',
        'slug': 'spisok-v-markdown',
        'publish': _at(2026, 11, 1),
        'tags': ['markdown'],
        'body': (
            'Маркдаун склеивает список с абзацем, если перед ним нет пустой строки.\n\n'
            '* Сначала пустая строка\n'
            '* Потом пункты\n'
        ),
    },
    {
        'title': 'Комментарий можно скрыть',
        'slug': 'kommentarii',
        'publish': _at(2026, 10, 20),
        'tags': ['комментарии'],
        'body': 'Новый комментарий виден сразу. Снять галку «Активный» в админке — и он пропадёт со страницы.',
        'comment': {
            'name': 'Анна',
            'email': 'anna@example.com',
            'body': 'Проверочный комментарий.',
        },
    },
    {
        'title': 'Пост со второй страницы',
        'slug': 'vtoraya-stranica',
        'publish': _at(2026, 10, 1),
        'tags': ['заметки'],
        'body': 'На странице списка по три поста. Этот остаётся на второй.',
    },
    {
        'title': 'Черновик',
        'slug': 'chernovik',
        'publish': _at(2026, 9, 1),
        'tags': [],
        'status': Post.Status.DRAFT,
        'body': 'Этого поста нет в списке, ленте и поиске.',
    },
]


class Command(BaseCommand):
    help = 'Добавляет примеры постов, если в блоге ещё ничего нет.'

    def handle(self, *args, **options):
        if Post.objects.exists():
            self.stdout.write('Посты уже есть, примеры не добавляю.')
            return

        author = self._author()
        for item in POSTS:
            post = Post.objects.create(
                title=item['title'],
                slug=item['slug'],
                author=author,
                body=item['body'],
                publish=item['publish'],
                status=item.get('status', Post.Status.PUBLISHED),
            )
            if item['tags']:
                post.tags.add(*item['tags'])
            comment = item.get('comment')
            if comment:
                Comment.objects.create(post=post, **comment)
        self.stdout.write(self.style.SUCCESS(f'Добавлено постов: {len(POSTS)}'))

    def _author(self):
        user_model = get_user_model()
        author = user_model.objects.filter(username='author').first()
        if author is not None:
            return author
        return user_model.objects.create_user(username='author', email='author@example.com')
