from django import template


register = template.Library()


@register.filter
def is_liked_by(instance, user):
    if user.is_authenticated:
        return instance.is_liked_by(user)
    return False


@register.filter
def is_disliked_by(instance, user):
    if user.is_authenticated:
        return instance.is_disliked_by(user)
    return False

