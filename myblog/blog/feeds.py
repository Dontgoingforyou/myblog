import markdown

from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from .models import Post


class LatestPostsFeed(Feed):
    title = 'Мой блог'
    link = '/blog/'
    description = 'Новые посты моего блога.'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        return item.publish
