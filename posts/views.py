from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'group.html',
        {'page': page, 'paginator': paginator, 'group': group}
    )


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'posts/new.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/new.html', {'form': form})


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    posts = user_profile.posts.all()
    count = posts.count()

    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    user = request.user
    following = user.is_authenticated and user_profile.following.exists()

    followers = user_profile.follower.count()
    followings = user_profile.following.count()

    return render(
        request, 'posts/profile.html',
        {
            'user_profile': user_profile,
            'username': username,
            'posts_count': count,
            'page': page,
            'paginator': paginator,
            'following': following,
            'followers': followers,
            'followings': followings
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm()
    following = (
        request.user.is_authenticated and 
        post.author.following.filter(user=request.user).exists() 
    )
    return render(
        request,
        'posts/post_view.html',
        {
            'user_profile': post.author,
            'username': username,
            'post': post,
            'posts_count': count,
            'items': comments,
            'following': following,
            'form': form
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect(
                'post',
                username=username,
                post_id=post_id
            )
        return render(
            request,
            'posts/post_edit.html',
            {'form': form, 'user': post.author, 'post': post}
        )
    form = PostForm(instance=post)
    return render(
        request,
        'posts/post_edit.html',
        {'form': form, 'user': post.author, 'post': post}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect(
                'post',
                username=username,
                post_id=post_id
            )
    form = CommentForm()
    return render(
        request,
        'posts/add_comment.html',
        {
            'post': post,
            'form': form
        }
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.values_list('author', flat=True)
    posts_list = Post.objects.filter(author__id__in=authors)

    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'posts/follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    user = request.user
    if (not Follow.objects.filter(user=user, author=author).exists() and
            author != user):
        Follow(user=user, author=author).save()
        return redirect(
            'profile',
            username=username
        )
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def profile_unfollow(request, username):
    user = request.user
    # Follow.objects.get(user=user, author=author).delete()
    get_object_or_404(Follow, author__username=username, user=user).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
