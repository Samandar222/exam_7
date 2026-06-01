from django.urls import path
from .views import (
    # Template views
    register_page, login_page, logout_page, profile_page,
    # API views
    RegisterView, LoginView, LogoutView, ProfileView, ProfileUpdateView,
)

urlpatterns = [
    # API endpoints
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login/',    LoginView.as_view(),    name='api-login'),
    path('logout/',   LogoutView.as_view(),   name='api-logout'),
    path('profile/',  ProfileView.as_view(),  name='api-profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='api-profile-update'),
]
