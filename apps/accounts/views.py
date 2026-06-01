from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

# DRF views (API)
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer

User = get_user_model()


# ============================================================
# TEMPLATE VIEWS  (HTML pages)
# ============================================================

def register_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not email or not password:
            error = 'All fields are required.'
        elif password != password_confirm:
            error = 'Passwords do not match.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters.'
        elif User.objects.filter(username=username).exists():
            error = 'Username is already taken.'
        elif User.objects.filter(email=email).exists():
            error = 'Email is already in use.'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('/')
    return render(request, 'accounts/register.html', {'error': error})


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            error = 'Invalid username or password.'
    return render(request, 'accounts/login.html', {'error': error})


def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('/login/')


@login_required(login_url='/login/')
def profile_page(request):
    success = False
    if request.method == 'POST':
        email  = request.POST.get('email', '').strip()
        bio    = request.POST.get('bio', '').strip()
        avatar = request.FILES.get('avatar')
        if email:
            request.user.email = email
        request.user.bio = bio
        if avatar:
            request.user.avatar = avatar
        request.user.save()
        success = True
    return render(request, 'accounts/profile.html', {'user': request.user, 'success': success})


# ============================================================
# API VIEWS  (JSON endpoints)
# ============================================================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Registration successful.',
            'user': {'id': user.id, 'username': user.username, 'email': user.email},
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful.',
            'user': {'id': user.id, 'username': user.username, 'email': user.email},
            'tokens': {'refresh': str(refresh), 'access': str(refresh.access_token)},
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            RefreshToken(refresh_token).blacklist()
            return Response({'message': 'Logout successful.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self): return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self): return self.request.user
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
