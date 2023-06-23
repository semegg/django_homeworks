from django.core.mail import send_mail
from django.urls import reverse


def send_activation_email(user, user_token, request):
    activation_url = f'http://{request.get_host()}{reverse("accounts:activate", args=[user.username, user_token.token])}'
    send_mail(
        'Activate your account',
        f'Please click on the following link to activate your account: {activation_url}',
        'noreply@example.com',
        [user.email],
        fail_silently=False
    )


def send_password_reset_email(user, user_token, request):
    activation_url = f'http://{request.get_host()}' \
                     f'{reverse("accounts:password_reset_done", args=[user.username, user_token.token])}'
    send_mail(
        'Reset password',
        f'Please click on the following link to reset your password: {activation_url}',
        'noreply@example.com',
        [user.email],
        fail_silently=False
    )

