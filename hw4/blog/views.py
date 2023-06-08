from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.text import slugify

from .forms import CommentForm, PostForm
from .models import (
    Post,
    PostLike,
    PostDislike,
    Comment,
    CommentLike,
    CommentDislike, Follow
)
from .utils import paginate_objects


def post_list(request):
    objects = Post.published.all()
    posts = paginate_objects(request, objects)
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post_slug):
    user = request.user
    post = get_object_or_404(Post,
                             slug=post_slug,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    form = CommentForm()
    follow = Follow.objects.filter(follower=user, followed=post.author) # ---------------
    if follow.exists():                                                 # немного подправлено тут
        follow = "Unfollow"
    else:
        follow = "Follow"
    return render(request, 'blog/post/detail.html', {'post': post, 'form': form, "follow": follow})


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.slug = slugify(post.title)
            post.save()
            return redirect(post.get_absolute_url())

    form = PostForm()
    return render(request, 'blog/post/create.html', {'form': form})


@login_required
def update_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return HttpResponseForbidden("You don't have permission to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title)
            post.save()
            return redirect(post.get_absolute_url())

    form = PostForm(instance=post)
    return render(request, 'blog/post/update.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return HttpResponseForbidden("You don't have permission to delete this post.")

    post.delete()
    return redirect('blog:post_list')


def post_category(request, category):
    objects = Post.published.filter(category__slug=category)
    posts = paginate_objects(request, objects)
    return render(request, 'blog/post/list.html', {'posts': posts})


def search_post(request):
    search_query = request.GET.get('search_query')
    search_param = request.GET.get('search_param')

    posts = Post.published.all()

    if search_query:
        if search_param == 'author':
            posts = posts.filter(author__username__icontains=search_query)
        elif search_param == 'post':
            posts = posts.filter(
                Q(title__icontains=search_query) | Q(body__icontains=search_query)
            )
    posts = paginate_objects(request, posts)
    return render(request, 'blog/post/list.html', {'posts': posts})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.is_liked_by(request.user):
        like = post.likes.get(user=request.user)
        like.delete()
    else:
        PostLike.objects.create(post=post, user=request.user)
        if post.is_disliked_by(request.user):
            dislike = post.dislikes.get(user=request.user)
            dislike.delete()
    return HttpResponseRedirect(f'{post.get_absolute_url()}#postFooter')


@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.is_disliked_by(request.user):
        dislike = post.dislikes.get(user=request.user)
        dislike.delete()
    else:
        PostDislike.objects.create(post=post, user=request.user)
        if post.is_liked_by(request.user):
            like = post.likes.get(user=request.user)
            like.delete()
    return HttpResponseRedirect(f'{post.get_absolute_url()}#postFooter')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
    return HttpResponseRedirect(f'{post.get_absolute_url()}#comments')


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.is_liked_by(request.user):
        like = comment.likes.get(user=request.user)
        like.delete()
    else:
        CommentLike.objects.create(comment=comment, user=request.user)
        if comment.is_disliked_by(request.user):
            dislike = comment.dislikes.get(user=request.user)
            dislike.delete()
    return HttpResponseRedirect(f'{comment.post.get_absolute_url()}#commentLike{comment.id}')


@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.is_disliked_by(request.user):
        dislike = comment.dislikes.get(user=request.user)
        dislike.delete()
    else:
        CommentDislike.objects.create(comment=comment, user=request.user)
        if comment.is_liked_by(request.user):
            like = comment.likes.get(user=request.user)
            like.delete()
    return HttpResponseRedirect(f'{comment.post.get_absolute_url()}#commentLike{comment.id}')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def delete_comment(comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return HttpResponseRedirect(f'{comment.post.get_absolute_url()}#comments')


@login_required
@user_passes_test(lambda user: user.is_superuser)
def toggle_comment_active(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.active = not comment.active
    comment.save()
    return HttpResponseRedirect(f'{comment.post.get_absolute_url()}#comments')


@login_required()
def follow_or_unfollow(request, post_id): # Интересно узнать чем опасно совмещать 2 эти действия в 1
    post = get_object_or_404(Post, id = post_id)
    user = request.user
    follow = Follow.objects.filter(follower=user, followed=post.author)
    if follow.exists():
        follower = post.author.followers.get(follower = user)
        follower.delete()
    else:
        Follow.objects.create(follower=user, followed=post.author)
    return redirect(post.get_absolute_url())
