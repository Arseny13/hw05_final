"""Подключение модулей."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, GroupForm, PostForm
from .models import Follow, Group, Post, User

COUNT_POSTS = 10


def paginator_page(request, posts: QuerySet) -> Page:
    """Функция для пагинации страниц."""
    paginator = Paginator(posts, COUNT_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Viev-функция главной страницы."""
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = paginator_page(request, posts)
    context = {
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Viev-функция страниц групп."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Viev-функция для страницы профиля."""
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    following = (not request.user.is_anonymous) and (
        Follow.objects.filter(
            user=request.user,
            author=user
        ).exists()
    )
    posts_list = user.posts.all()
    page_obj = paginator_page(request, posts_list)
    context = {
        'author': user,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Viev-функция страниц поста."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comment_list = post.comments.all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comment_list,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Viev-функция для создания поста."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            reverse('posts:profile', args=[request.user.username])
        )
    return render(request, template, {'form': form})


@login_required
def group_create(request):
    """Viev-функция для создания группы."""
    template = 'posts/create_group.html'
    form = GroupForm(request.POST or None)
    if form.is_valid():
        group = form.save(commit=False)
        group.save()
        return redirect(
            reverse('posts:group_list', args=[group.slug])
        )
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Viev-функция для редактирования поста."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            reverse('posts:post_detail', args=[post.id])
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            reverse('posts:post_detail', args=[post.id])
        )
    context = {
        'is_edit': True,
        'id': post.id,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_delete(request, post_id):
    template = 'posts/post_delete.html'
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect(
            reverse('posts:post_detail', args=[post.id])
        )
    id = post.id
    context = {
        'is_edit': True,
        'id': id,
    }
    post.delete()
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Viev-функция для редактирования поста."""
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Viev-функция для подписок."""
    template = 'posts/follow.html'
    user = request.user
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_page(request, posts_list)
    context = {
        'author': user,
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Viev-функция для оформления подписки."""
    user = request.user
    follow = get_object_or_404(User, username=username)
    if follow != user:
        Follow.objects.get_or_create(
            user=user,
            author=follow
        )
    return redirect(reverse('posts:follow_index'))


@login_required
def profile_unfollow(request, username):
    """Viev-функция для отписки."""
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=author,
    )
    follow.delete()
    return redirect(reverse('posts:follow_index'))
