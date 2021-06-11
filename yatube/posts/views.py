from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)
    return render(
        request,
        'index.html',
        {'page': page}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)

    return render(request, 'group.html',
                  {'group': group, 'page': page, 'paginator': paginator})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.user_posts.all()
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
        return render(
            request,
            'profile.html',
            {'page': page, 'paginator': paginator,
             'author': author, 'following': following}
        )
    return render(request, 'profile.html',
                  {'page': page, 'paginator': paginator, 'author': author})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=profile)
    post_count = profile.user_posts.all().count()
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        'post.html',
        {'post': post, 'author': profile, 'post_count': post_count,
         'comments': comments, 'form': form}
    )


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new_post.html', {'form': form})
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form, 'add': True})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related('author'),
                             id=post_id, author__username=username)

    if request.user != post.author:
        return redirect('post', username, post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post', username=request.user.username,
                            post_id=post_id)

    return render(
        request, 'new_post.html', {'form': form, 'post': post, 'edit': True}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'comments.html', {'form': form, 'post': post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)
    return render(request, 'follow.html',
                  {'page': page, 'posts': posts})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow_obj = Follow.objects.filter(user=request.user, author=author)
    if request.user != author and follow_obj.exists() is False:
        Follow.objects.create(user=request.user, author=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_obj = get_object_or_404(
        Follow, user=request.user,
        author=author
    )
    follow_obj.delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
