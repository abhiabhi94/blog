from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Users import views as user_views
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView
from . import views

app_name = 'Blog'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('about', views.about, name='about'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='Users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='Users/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/preview/<slug:slug>', views.preview, name='post-preview'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<slug:slug>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete', PostDeleteView.as_view(), name='post-delete'),
    
    ]

