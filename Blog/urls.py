from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Users import views as user_views
from .import views
from Track.views import hit_count


app_name = 'Blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),  
    path('user/<str:username>', views.UserPostListView.as_view(), name='user-posts'),
    path('user/<str:username>/bookmarks', views.UserPostBookmark.as_view(), name='user-bookmarks'),
    path('<str:username>/posts', views.UserPostListView.as_view(), name='my-posts'),
    path('about', views.about, name='about'),
    path('post/new', views.PostCreateView.as_view(), name='post-create'),
    path('post/preview/<slug:slug>', views.preview, name='post-preview'),
    path('post/<slug:slug>', hit_count(views.PostDetailView.as_view()), name='post-detail'),
    path('post/<slug:slug>/update', views.PostUpdateView.as_view(), name='post-update'),
    path('post/<slug:slug>/delete', views.PostDeleteView.as_view(), name='post-delete'),
    path('post/tag/<str:tag>', views.TaggedPostListView.as_view(), name='tagged'),
    path('post/bookmark', views.bookmark_post, name='bookmark-post'),
    path('post/tag/', views.get_tags, name='all-tags'), 
    path('post/top-tags/', views.get_top_tags, name='top-tags'),
    ]

