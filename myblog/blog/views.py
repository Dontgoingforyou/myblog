import logging
import secrets
import threading

from django.contrib import messages
from django.contrib.postgres.search import TrigramWordSimilarity
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.db.models.functions import Greatest, Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django.core.mail import send_mail
from django.conf import settings
from taggit.models import Tag
from .models import Comment, Post
from .forms import EmailPostForm, CommentForm, SearchForm

logger = logging.getLogger(__name__)


class PostListView(ListView):
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        qs = Post.published.select_related('author').prefetch_related('tags')
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
            Post.published.select_related('author'),
            slug=self.kwargs['post'],
            publish__year=self.kwargs['year'],
            publish__month=self.kwargs['month'],
            publish__day=self.kwargs['day'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        comments = list(post.comments.filter(active=True).select_related('parent'))
        threads = comment_threads(comments)
        author = _comment_author(self.request)
        context['comments'] = threads
        context['comments_count'] = sum(1 + len(item.thread_replies) for item in threads)
        context['comment_name'] = author['name']
        context['comment_email'] = author['email']
        context['comment_token'] = _comment_token(self.request)
        context['form'] = CommentForm(initial=author)
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
            threading.Thread(
                target=deliver_share_mail,
                args=(subject, message, settings.DEFAULT_FROM_EMAIL, cd['to']),
                daemon=True,
            ).start()
            logger.info('Письмо со ссылкой на пост %s поставлено в отправку', post.id)
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def comment_threads(comments):
    """Собирает ветки. Ответ на скрытый комментарий не становится новым корнем."""
    nodes = {comment.id: comment for comment in comments}
    for comment in comments:
        comment.thread_replies = []
    roots = []
    for comment in comments:
        root = comment
        seen = set()
        visible = True
        while root.parent_id and root.id not in seen:
            if root.parent_id not in nodes:
                visible = False
                break
            seen.add(root.id)
            root = nodes[root.parent_id]
        if not visible:
            continue
        if root is comment:
            roots.append(comment)
        else:
            root.thread_replies.append(comment)
    return roots


def deliver_share_mail(subject, message, sender, recipient):
    try:
        send_mail(subject, message, sender, [recipient])
    except Exception:
        logger.exception('Не удалось отправить письмо со ссылкой на пост')


def _reply_parent(post, parent_id):
    if not parent_id:
        return None
    return get_object_or_404(Comment, id=parent_id, post=post, active=True)


def _comment_author(request):
    return {
        'name': request.session.get('comment_name', ''),
        'email': request.session.get('comment_email', ''),
    }


def _remember_comment_author(request, comment):
    request.session['comment_name'] = comment.name
    request.session['comment_email'] = comment.email


def _comment_token(request):
    token = request.session.get('comment_token')
    if not token:
        token = secrets.token_urlsafe(16)
        request.session['comment_token'] = token
    return token


def _rotate_comment_token(request):
    request.session['comment_token'] = secrets.token_urlsafe(16)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    parent = _reply_parent(post, request.POST.get('parent'))
    token = request.POST.get('token', '')
    if not token or token != request.session.get('comment_token'):
        logger.info('Повтор комментария к посту %s', post.id)
        messages.info(request, 'Комментарий уже отправлен.')
        return redirect(post.get_absolute_url())
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.parent = parent
        comment.submit_token = token
        try:
            with transaction.atomic():
                comment.save()
        except IntegrityError:
            logger.info('Повтор комментария к посту %s', post.id)
            messages.info(request, 'Комментарий уже отправлен.')
            return redirect(post.get_absolute_url())
        _remember_comment_author(request, comment)
        _rotate_comment_token(request)
        logger.info('Комментарий %s к посту %s', comment.id, post.id)
        text = 'Ответ добавлен.' if parent else 'Комментарий добавлен.'
        messages.success(request, text)
        return redirect(f'{post.get_absolute_url()}#comment-{comment.id}')
    logger.info('Комментарий к посту %s не прошёл проверку', post.id)
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'parent': parent,
            'comment_token': _comment_token(request),
        },
    )


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
