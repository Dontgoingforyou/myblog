import markdown

from django.utils.safestring import mark_safe
from django import template
from django.db.models import Count, Q
from ..models import Post

register = template.Library()


@register.filter
def russian_pluralize(number, forms):
    """Возвращает одну из трёх форм слова по русским правилам склонения."""
    one, few, many = (form.strip() for form in forms.split(','))
    number = abs(int(number))
    last_two = number % 100
    last_one = number % 10

    if last_one == 1 and last_two != 11:
        return one
    if 2 <= last_one <= 4 and last_two not in {12, 13, 14}:
        return few
    return many


@register.simple_tag
def page_url(request, number):
    """Ссылка на страницу с остальными параметрами запроса, не только page."""
    params = request.GET.copy()
    params['page'] = number
    return f'?{params.urlencode()}'


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments', filter=Q(comments__active=True)),
    ).order_by('-total_comments', '-publish')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    """Текст поста из админки, HTML не экранируется."""
    return mark_safe(markdown.markdown(text))
