from rest_framework import serializers
from .models import Category, Post, Comment, Like


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Category name must be at least 2 characters.')
        return value.strip()


class PostListSerializer(serializers.ModelSerializer):
    author         = serializers.StringRelatedField()
    category       = serializers.StringRelatedField()
    likes_count    = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'image', 'author', 'category', 'likes_count', 'comments_count', 'created_at']


class PostDetailSerializer(serializers.ModelSerializer):
    author         = serializers.StringRelatedField()
    category       = serializers.StringRelatedField()
    likes_count    = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'author', 'category',
                  'likes_count', 'comments_count', 'created_at', 'updated_at']


class PostWriteSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'image', 'category']

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError('Title must be at least 5 characters.')
        return value.strip()

    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('Content must be at least 10 characters.')
        return value.strip()

    def validate_image(self, value):
        if value is None:
            return value
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image file size must be under 2 MB.')
        allowed = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(value, 'content_type') and value.content_type not in allowed:
            raise serializers.ValidationError('Only JPEG, PNG, and WebP images are allowed.')
        return value


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError('Comment cannot be empty.')
        if len(value) > 1000:
            raise serializers.ValidationError('Comment cannot exceed 1000 characters.')
        return value.strip()


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post']
        read_only_fields = ['id', 'user']
