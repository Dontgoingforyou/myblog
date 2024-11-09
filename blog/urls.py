from django.urls import path

from blog.apps import BlogConfig
from blog.views import post_list, post_detail, post_share, post_comment, post_search
from blog.feeds import LatestPostFeed

app_name = BlogConfig.name

urlpatterns = [
    path('', post_list, name='post_list'),
    path('tag/<str:tag_slug>/', post_list, name='post_list_by_tag'),
    path('<int:day>/<int:month>/<int:year>/<slug:post>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/',post_share, name='post_share'),
    path('<int:post_id>/comment/', post_comment, name='post_comment'),
    path('feed/', LatestPostFeed(), name='post_feed'),
    path('search/', post_search, name='post_search'),
]