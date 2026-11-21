from django.shortcuts import render, get_object_or_404
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db.models import Count
from django.db.models.functions import Greatest, Lower
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm


class PostListView(ListView):
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        qs = Post.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            qs = qs.filter(tags__in=[self.tag])
        else:
            self.tag = None
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=self.kwargs['post'],
            publish__year=self.kwargs['year'],
            publish__month=self.kwargs['month'],
            publish__day=self.kwargs['day'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = post.comments.filter(active=True)
        context['form'] = CommentForm()
        context['similar_posts'] = self._similar_posts(post)
        return context

    def _similar_posts(self, post):
        tag_ids = post.tags.values_list('id', flat=True)
        similar = Post.published.filter(tags__in=tag_ids).exclude(id=post.id)
        return similar.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} рекомендует вам прочитать {post.title}"
            message = f"Прочитайте {post.title} по ссылке: {post_url}\n\n{cd['name']} комментирует: {cd['comments']}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(
                similarity=Greatest(
                    TrigramWordSimilarity(query, Lower('title')),
                    TrigramWordSimilarity(query, Lower('body')),
                ),
            ).filter(similarity__gt=0.4).order_by('-similarity')
        else:
            results = []
    return render(
        request,
        'blog/post/search.html',
        {'form': form, 'query': query, 'results': results},
    )
