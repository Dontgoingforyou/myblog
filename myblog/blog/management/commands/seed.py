from datetime import datetime
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image

from blog.models import Comment, Post


def _at(year, month, day):
    return timezone.make_aware(datetime(year, month, day, 12, 0))


POSTS = [
    {
        'title': 'Поиск по слову, а не по всей строке',
        'slug': 'poisk-po-slovu',
        'publish': _at(2026, 11, 2),
        'tags': ['поиск', 'postgresql'],
        'summary': 'Короткое слово ищется внутри заголовка и текста, а не по всей фразе сразу.',
        'cover': True,
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
        'comments': [
            {
                'name': 'Анна',
                'email': 'anna@example.com',
                'body': 'Проверочный комментарий.',
            },
        ],
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
    help = 'Добавляет недостающие примеры. Уже написанные посты не трогает.'

    def handle(self, *args, **options):
        author = self._author()
        created = 0
        for item in POSTS:
            post, was_created = self._post(author, item)
            created += int(was_created)
            for comment in item.get('comments', []):
                self._comment(post, comment)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Добавлено постов: {created}'))
            return
        self.stdout.write('Примеры уже на месте.')

    def _post(self, author, item):
        post = Post.objects.filter(slug=item['slug'], publish__date=item['publish'].date()).first()
        if post is None:
            post = Post.objects.create(
                title=item['title'],
                slug=item['slug'],
                author=author,
                summary=item.get('summary', ''),
                body=item['body'],
                publish=item['publish'],
                status=item.get('status', Post.Status.PUBLISHED),
            )
            if item['tags']:
                post.tags.add(*item['tags'])
            if item.get('cover'):
                post.cover.save('sample-cover.png', self._cover(), save=True)
            return post, True
        return post, False

    def _comment(self, post, data):
        if post.comments.filter(name=data['name'], body=data['body']).exists():
            return
        Comment.objects.create(
            post=post,
            name=data['name'],
            email=data['email'],
            body=data['body'],
        )

    def _cover(self):
        buffer = BytesIO()
        Image.new('RGB', (1200, 675), (143, 61, 50)).save(buffer, 'PNG')
        return ContentFile(buffer.getvalue())

    def _author(self):
        user_model = get_user_model()
        author = user_model.objects.filter(username='author').first()
        if author is not None:
            return author
        return user_model.objects.create_user(username='author', email='author@example.com')
