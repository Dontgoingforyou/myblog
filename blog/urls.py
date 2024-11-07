from django.urls import path

from blog.apps import BlogConfig
from blog.views import post_list, post_detail

app_name = BlogConfig.name

urlpatterns = [
    path('', post_list, name='post_list'),
    path('<int:id>/', post_detail, name='post_detail'),
]