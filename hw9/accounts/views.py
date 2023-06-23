from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, authenticate, logout, update_session_auth_hash
from django.contrib import messages

from .forms import (
    RegisterForm,
    LoginForm,
    ReactivationForm,
    PasswordResetForm,
    PasswordSetForm,
    ProfileForm,
    ChangePasswordForm
)
from .models import ActivationToken, PasswordResetToken, Profile
from blog.models import Post, Follow
from .utils import send_activation_email, send_password_reset_email


User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already have account')
        return redirect('blog:post_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            user_token = ActivationToken.objects.create(user=user)
            send_activation_email(user, user_token, request)
            messages.success(request, 'You have to activate your account')
            return redirect('blog:post_list')
        else:
            context = {
                'form': form,
                'form_errors': form.errors
            }
            return render(request, 'accounts/register.html', context)

    form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def activate_account_view(request, username, token):
    user = get_object_or_404(User, username=username)
    token = get_object_or_404(ActivationToken, user=user, token=token)

    if user.is_active:
        messages.error(request, 'User is already activated')
        return redirect('blog:post_list')

    if token.verify_token():
        user.is_active = True
        token.delete()
        user.save()

        messages.success(request, 'Activation complete')
        return redirect('accounts:login')

    messages.error(request, 'Token expired')
    return redirect('accounts:login')


def reactivation_sent_view(request):
    if request.method == 'POST':
        form = ReactivationForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])

            if user.is_active:
                messages.warning(request, 'This account is already activate.')
                return redirect('accounts:login')

            old_token = ActivationToken.objects.filter(user=user).first()
            if old_token:
                old_token.delete()

            new_token = ActivationToken.objects.create(user=user)

            send_activation_email(user, new_token, request)
            messages.success(request, 'Reactivation token has been sent. Please check your email inbox.')
            return redirect('accounts:reactivate_sent')
        else:
            context = {'form': form, 'form_errors': form.errors}
            return render(request, 'accounts/reactivation_sent.html', context)

    form = ReactivationForm()
    return render(request, 'accounts/reactivation_sent.html', {'form': form})


def password_reset_sent_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])

            if not user.is_active:
                messages.warning(request, 'This account is not activate.')
                return redirect('accounts:login')

            old_token = PasswordResetToken.objects.filter(user=user).first()
            if old_token:
                old_token.delete()

            new_token = PasswordResetToken.objects.create(user=user)

            send_password_reset_email(user, new_token, request)
            messages.success(request, 'Password rest token has been sent. Please check your email inbox.')
            return redirect('accounts:password_reset_sent')
        else:
            context = {'form': form, 'form_errors': form.errors}
            return render(request, 'accounts/password_reset_sent.html', context)

    form = PasswordResetForm()
    return render(request, 'accounts/password_reset_sent.html', {'form': form})


def password_reset_done_view(request, username, token):
    user = get_object_or_404(User, username=username)
    token = get_object_or_404(PasswordResetToken, user=user, token=token)

    if request.method == 'POST':
        form = PasswordSetForm(user, data=request.POST)
        if form.is_valid():
            form.save()
            token.delete()
            messages.success(request, 'Your password has been updated.')
            return redirect('accounts:login')
        else:
            context = {'form': form, 'form_errors': form.errors}
            return render(request, 'accounts/password_reset_done.html', context)

    form = PasswordSetForm(user)
    return render(request, 'accounts/password_reset_done.html', {'form': form})


@login_required
def change_password_view(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        raise PermissionDenied(f"You don't have permission to change password for user - {user.username}")

    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated')
            return redirect('accounts:profile_detail', username=username)
        else:
            context = {'form': form, 'form_errors': form.errors}
            return render(request, 'accounts/change_password.html', context)

    form = ChangePasswordForm(user)
    return render(request, 'accounts/change_password.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in')
        return redirect('blog:post_list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            user = authenticate(request, email=email, password=password)

            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 7)

            if user is not None:
                login(request, user)
                return redirect('blog:post_list')
            else:
                messages.error(request, 'Invalid email or password')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid form data')
            return redirect('accounts:login')

    form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile_create_view(request):
    if hasattr(request.user, 'profile'):
        messages.info(request, 'You already have profile')
        return redirect('blog:post_list')

    if request.method == 'POST':
        form = ProfileForm(request.POST)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('blog:post_list')
        else:
            context = {
                'form': form,
                'form_errors': form.errors
            }
            return render(request, 'accounts/profile/create.html', context)

    form = ProfileForm()
    return render(request, 'accounts/profile/create.html', {'form': form})


@login_required
def profile_update_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    if request.user != profile.user:
        raise PermissionDenied("You don't have permission to edit this profile")

    if request.method == 'POST':
        form = ProfileForm(instance=profile, data=request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated')
            return redirect('accounts:profile_detail', username=profile.user.username)
        else:
            context = {
                'form': form,
                'form_errors': form.errors
            }
            return render(request, 'accounts/profile/update.html', context)

    form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile/update.html', {'form': form})


def profile_detail_view(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    posts = Post.published.filter(author=profile.user)[:4]
    context = {
        'profile': profile,
        'posts': posts
    }
    return render(request, 'accounts/profile/detail.html', context)


@login_required
def follow_user_view(request, username):
    followed_user = get_object_or_404(User, username=username)
    follower_user = request.user

    print(request.META.get('HTTP_REFERER', '/'))

    follow, created = Follow.objects.get_or_create(follower=follower_user, followed=followed_user)
    if not created:
        messages.warning(request, f'You are already following {follow.followed.username}')
    else:
        messages.success(request, f'You are now following {follow.followed.username}')
    profile_url = redirect('accounts:profile_detail', username=followed_user.username)
    return redirect(request.META.get('HTTP_REFERER', profile_url))


@login_required
def unfollow_user_view(request, username):
    followed_user = get_object_or_404(User, username=username)
    follower_user = request.user

    follow = Follow.objects.filter(follower=follower_user, followed=followed_user).first()
    if follow:
        messages.success(request, f'You have unfollowed {followed_user.username}')
        follow.delete()
    else:
        messages.warning(request, f'You are not following {followed_user.username}')
    profile_url = redirect('accounts:profile_detail', username=followed_user.username)
    return redirect(request.META.get('HTTP_REFERER', profile_url))


def followers_list_view(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    profile = user.profile
    context = {
        'followers': followers,
        'profile': profile
    }
    return render(request, 'accounts/profile/followers.html', context)


def following_list_view(request, username):
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    profile = user.profile
    context = {
        'followings': following,
        'profile': profile
    }
    return render(request, 'accounts/profile/following.html', context)

