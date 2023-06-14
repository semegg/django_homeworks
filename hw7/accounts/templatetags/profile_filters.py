from datetime import datetime, date

from django import template

from blog.models import Follow

register = template.Library()


@register.filter
def calculate_age(born):
    today = date.today()
    birth_date = datetime.strptime(str(born), "%Y-%m-%d").date()
    age = today.year - birth_date.year
    return age


@register.filter
def is_following(follower, followed):
    follow = Follow.objects.filter(follower=follower, followed=followed)
    return follow.exists()


@register.filter
def is_followed_by(followed, follower):
    follow = Follow.objects.filter(follower=follower, followed=followed)
    return follow.exists()

