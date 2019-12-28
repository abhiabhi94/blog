from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from Users import views as user_views
from .import views

app_name = 'Blog'

ymds_re = r'(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<slug>[-\w]+)'
ymd_re = r'(?P<year>[0-9]{4})/?(?P<month>[0-9]{1,2})?/?(?P<day>[0-9]{1,2})?'

urlpatterns = [
    # path('', views.PostListView.as_view(), name='home'),
    path('', views.HomeView.as_view(), name='home'),
    path('subscribe/', views.subscribe, name='subscription'),
    path('user/<str:username>', views.UserPostListView.as_view(), name='user-posts'),
    path('user/<str:username>/bookmarks',
         views.UserPostBookmark.as_view(), name='user-bookmarks'),
    path('<str:username>/posts', views.UserPostListView.as_view(), name='my-posts'),
    path('about', views.about, name='about'),
    path('post/new', views.PostCreateView.as_view(), name='post-create'),
    # path('post/preview/<slug:slug>', views.preview, name='post-preview'),
    # path('post/<slug:slug>', hit_count(views.PostDetailView.as_view()), name='post-detail'),
    # path('post/<slug:slug>/update', views.PostUpdateView.as_view(), name='post-update'),
    # path('post/<slug:slug>/delete', views.PostDeleteView.as_view(), name='post-delete'),
    re_path(r'post/preview/'+ymds_re+'$', views.preview, name='post-preview'),
    re_path(r'post/'+ymds_re+'$',
            views.PostDetailView.as_view(), name='post-detail'),
    re_path(r'post/'+ymds_re+'/update$',
            views.PostUpdateView.as_view(), name='post-update'),
    re_path(r'post/'+ymds_re+'/delete$',
            views.PostDeleteView.as_view(), name='post-delete'),
    path('post/recommended-posts', views.get_recommended_posts,
         name='recommended-posts'),
    path('post/bookmark/', views.bookmark_post, name='bookmark-post'),
    path('post/tag', views.get_tags, name='all-tags'),
    path('post/tag/<str:tag>', views.TaggedPostListView.as_view(), name='tagged'),
    path('post/featured-posts/',
         views.FeaturedPostListView.as_view(), name='featured-posts'),
    path('post/latest-posts/', views.get_latest_posts, name='latest-posts'),
    path('post/trending-posts/', views.get_trending_posts, name='trending-posts'),
    path('post/category', views.get_category, name='all-categories'),
    path('post/category/<slug:slug>',
         views.CategoryPostListView.as_view(), name='categorised'),
    re_path(r'post/'+ymd_re+'$', views.get_timewise_list, name='timewise-list'),
]
