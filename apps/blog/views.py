from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

# DRF
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.pagination import StandardPagination
from .filters import PostFilter
from .models import Category, Post, Comment, Like
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CategorySerializer, PostListSerializer,
    PostDetailSerializer, PostWriteSerializer,
    CommentSerializer, LikeSerializer,
)


# ============================================================
# TEMPLATE VIEWS  (HTML pages)
# ============================================================

def post_list_page(request):
    posts = Post.objects.select_related('author', 'category') \
                        .prefetch_related('likes', 'comments') \
                        .order_by('-created_at')

    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '').strip()

    if search:
        posts = posts.filter(title__icontains=search)
    if category_id:
        posts = posts.filter(category__id=category_id)

    categories = Category.objects.all()
    return render(request, 'blogs/post_list.html', {
        'posts': posts,
        'categories': categories,
    })


def post_detail_page(request, pk):
    post = get_object_or_404(
        Post.objects.select_related('author', 'category')
                    .prefetch_related('likes', 'comments__user'),
        pk=pk
    )

    # Like toggle
    if request.method == 'POST' and request.user.is_authenticated:
        action_name = request.POST.get('action')
        if action_name == 'like':
            Like.objects.get_or_create(user=request.user, post=post)
        elif action_name == 'unlike':
            Like.objects.filter(user=request.user, post=post).delete()
        elif action_name == 'comment':
            text = request.POST.get('text', '').strip()
            if text:
                Comment.objects.create(user=request.user, post=post, text=text)
        return redirect(f'/posts/{pk}/')

    user_liked = request.user.is_authenticated and \
                 Like.objects.filter(user=request.user, post=post).exists()

    return render(request, 'blogs/post_detail.html', {
        'post': post,
        'user_liked': user_liked,
    })


@login_required(login_url='/login/')
def post_create_page(request):
    categories = Category.objects.all()
    error = None
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        content  = request.POST.get('content', '').strip()
        cat_id   = request.POST.get('category', '').strip()
        image    = request.FILES.get('image')

        if not title or not content or not cat_id:
            error = 'Title, content and category are required.'
        elif len(title) < 5:
            error = 'Title must be at least 5 characters.'
        elif len(content) < 10:
            error = 'Content must be at least 10 characters.'
        else:
            category = get_object_or_404(Category, pk=cat_id)
            post = Post.objects.create(
                title=title, content=content,
                category=category, author=request.user,
                image=image if image else None,
            )
            messages.success(request, 'Post published successfully!')
            return redirect(f'/posts/{post.pk}/')

    return render(request, 'blogs/post_create.html', {'categories': categories, 'error': error})


@login_required(login_url='/login/')
def post_update_page(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You are not allowed to edit this post.')
        return redirect(f'/posts/{pk}/')

    categories = Category.objects.all()
    error = None
    if request.method == 'POST':
        title   = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        cat_id  = request.POST.get('category', '').strip()
        image   = request.FILES.get('image')

        if not title or not content or not cat_id:
            error = 'All fields are required.'
        elif len(title) < 5:
            error = 'Title must be at least 5 characters.'
        else:
            post.title   = title
            post.content = content
            post.category = get_object_or_404(Category, pk=cat_id)
            if image:
                post.image = image
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect(f'/posts/{post.pk}/')

    return render(request, 'blogs/post_update.html', {
        'post': post, 'categories': categories, 'error': error
    })


@login_required(login_url='/login/')
def post_delete_page(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You are not allowed to delete this post.')
        return redirect(f'/posts/{pk}/')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully.')
        return redirect('/posts/')

    return render(request, 'blogs/post_delete.html', {'post': post})


# ============================================================
# API VIEWSETS  (JSON endpoints)
# ============================================================

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author', 'category') \
                           .prefetch_related('comments', 'likes')
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardPagination
    filterset_class = PostFilter
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return PostWriteSerializer
        return PostDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        _, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response({'detail': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Liked.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        deleted, _ = Like.objects.filter(user=request.user, post=post).delete()
        if not deleted:
            return Response({'detail': 'Not liked.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Like removed.'}, status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user', 'post').order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = super().get_queryset()
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post__id=post_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
