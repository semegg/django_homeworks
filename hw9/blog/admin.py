from django.contrib import admin

from .models import (
    Category,
    Post,
    PostLike,
    PostDislike,
    Comment,
    CommentLike,
    CommentDislike,
    Follow
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    search_fields = ('title', 'body')
    list_filter = ('status', 'created', 'author')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-status', '-publish')
    raw_id_fields = ('author',)


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')
    search_fields = ('post__author__username', 'user__username')


@admin.register(PostDislike)
class PostDislikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')
    search_fields = ('post__author__username', 'user__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('author__username', 'body')
    actions = ['activate_comments', 'deactivate_comments']

    def activate_comments(self, request, queryset):
        queryset.update(active=True)

    def deactivate_comments(self, request, queryset):
        queryset.update(active=False)


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user')
    search_fields = ('comment__author__username', 'user__username')


@admin.register(CommentDislike)
class CommentDislikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user')
    search_fields = ('comment__author__username', 'user__username')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed', 'created')
    list_filter = ('follower', 'followed', 'created')
