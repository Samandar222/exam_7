from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Template views
from apps.accounts.views import register_page, login_page, logout_page, profile_page
from apps.blog.views import (
    post_list_page, post_detail_page,
    post_create_page, post_update_page, post_delete_page,
)

# Home view
from django.shortcuts import render
from apps.blog.models import Post

def home(request):
    posts = Post.objects.select_related('author', 'category') \
                        .prefetch_related('likes', 'comments') \
                        .order_by('-created_at')[:6]
    total_posts = Post.objects.count()
    return render(request, 'home.html', {'posts': posts, 'total_posts': total_posts})


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # ---- HTML Pages ----
    path('',                home,               name='home'),
    path('register/',       register_page,      name='register'),
    path('login/',          login_page,         name='login'),
    path('logout/',         logout_page,        name='logout'),
    path('profile/',        profile_page,       name='profile'),

    path('posts/',              post_list_page,   name='post-list'),
    path('posts/create/',       post_create_page, name='post-create'),
    path('posts/<int:pk>/',     post_detail_page, name='post-detail'),
    path('posts/<int:pk>/update/', post_update_page, name='post-update'),
    path('posts/<int:pk>/delete/', post_delete_page, name='post-delete'),

    # ---- REST API ----
    path('api/auth/', include('apps.accounts.urls')),
    path('api/',      include('apps.blog.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
