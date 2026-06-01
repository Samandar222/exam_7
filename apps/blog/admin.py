from django.contrib import admin

from .models import (
    Category,
    Post,
    Comment,
    Like
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ['id', 'name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'title',
        'author',
        'category',
        'created_at'
    ]

    list_filter = ['category']

    search_fields = ['title']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'user',
        'post',
        'created_at'
    ]


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'user',
        'post'
    ]