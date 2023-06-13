from django.db import models


class PostPublishedManager(models.Manager):
    def get_queryset(self):
        return (super(PostPublishedManager, self)
                .get_queryset()
                .filter(status='published'))




