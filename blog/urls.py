from django.urls import path

from blog.apps import BlogConfig
from blog.views import PostListView, post_detail, post_share, post_comment

app_name = BlogConfig.name

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:day>/<int:month>/<int:year>/<slug:post>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/',post_share, name='post_share'),
    path('<int:post_id>/comment/', post_comment, name='post_comment'),
]