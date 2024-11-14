from django import template
from django.db.models import Count
from blog.models import Post
from django.utils.safestring import mark_safe

import markdown

register = template.Library()


@register.filter
def russian_pluralize(value, arg=None):
    forms = arg.split(',')
    if not forms or len(forms) != 3:
        return ''

    try:
        value = abs(int(value))
    except (TypeError, ValueError):
        return forms[2]

    if value % 10 == 1 and value % 100 != 11:
        form = forms[0]
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        form = forms[1]
    else:
        form = forms[2]
    return form


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def get_most_commented_posts(count=2):
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=3):
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}
