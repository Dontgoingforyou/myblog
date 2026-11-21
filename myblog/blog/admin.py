from django.contrib import admin
from .models import Comment, Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    readonly_fields = ['for_body']

    @admin.display(description='Для текста поста')
    def for_body(self, obj):
        if not obj.image:
            return ''
        return f'![]({obj.image.url})'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created_at', 'publish', 'author']
    search_fields = ['title', 'summary', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    show_facets = admin.ShowFacets.ALWAYS
    inlines = [PostImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'post', 'parent', 'created_at', 'active']
    list_filter = ['active', 'created_at', 'updated_at']
    search_fields = ['name', 'email', 'body']
    ordering = ['created_at']
    raw_id_fields = ['post', 'parent']
    show_facets = admin.ShowFacets.ALWAYS
