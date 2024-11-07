from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']  # боковая панель поиска
    search_fields = ['title', 'body']  # строка поиска
    prepopulated_fields = {'slug': ('title',)}  # автоматическое заполнение slug
    raw_id_fields = ['author']  # поисковый виджет
    date_hierarchy = 'publish'  # навигация по датам
    ordering = ['status', 'publish']  # сортировка
    show_facets = admin.ShowFacets.ALWAYS  # Фасетные фильтры