from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Users import views as user_views
from .views import (about,
                    PostListView,
                    PostDetailView,
                    PostCreateView,
                    PostUpdateView,
                    PostDeleteView,
                    UserPostListView,
                    preview,
                    bookmark_post,
                    )

app_name = 'Blog'

urlpatterns = [
    path('', PostListView.as_view(), name='home'),  
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('about', about, name='about'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/preview/<slug:slug>', preview, name='post-preview'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<slug:slug>/update', PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('post/bookmark', bookmark_post, name='bookmark-post'),
    ]

