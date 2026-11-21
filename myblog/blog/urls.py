from django.urls import path, register_converter
from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'


class UnicodeSlugConverter:
    """Стандартный slug в адресе — только ASCII, кириллический тег им не открыть."""

    regex = r'[-\w]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, 'uslug')

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('tag/<uslug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
]
