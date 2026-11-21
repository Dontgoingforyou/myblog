from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField('Заголовок', max_length=250)
    slug = models.SlugField('Слаг', max_length=250, unique_for_date='publish')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='Автор'
        )
    summary = models.CharField('Краткое описание', max_length=300, blank=True)
    body = models.TextField('Текст')
    cover = models.ImageField('Обложка', upload_to='covers/%Y/%m/%d/', blank=True)
    publish = models.DateTimeField('Дата публикации', default=timezone.now)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    status = models.CharField('Статус', max_length=2, choices=Status.choices, default=Status.DRAFT)
    objects = models.Manager()
    published = PublishedManager()
    tags = TaggableManager()

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month, self.publish.day, self.slug])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField('Имя', max_length=80)
    email = models.EmailField('Email')
    body = models.TextField('Текст')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    active = models.BooleanField('Активный', default=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комментарий {self.name} на {self.post}'


class PostImage(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Пост',
    )
    image = models.ImageField('Изображение', upload_to='posts/%Y/%m/%d/')

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.image.name
