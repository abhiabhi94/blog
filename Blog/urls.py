from django.urls import path, re_path

from Blog import views

app_name = 'Blog'

ymds_re = r'(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/(?P<day>[0-9]{1,2})/(?P<slug>[-\w]+)/'
ymd_re = r'(?P<year>[0-9]{4})/?(?P<month>[0-9]{1,2})?/?(?P<day>[0-9]{1,2})?/'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('subscribe/', views.subscribe, name='subscription'),
    path('author/<str:username>/',
         views.AuthorPostListView.as_view(), name='author-posts'),
    path('user/<str:username>/bookmarks/',
         views.UserPostBookmark.as_view(), name='user-bookmarks'),
    path('user/<str:username>/posts/<str:tab>/',
         views.UserPostListView.as_view(), name='my-posts'),
    path('about/', views.about, name='about'),
    path('post/new/', views.PostCreateView.as_view(), name='post-create'),
    path(
        'post/draft/<slug:slug>/',
        views.DraftPostUpdateView.as_view(),
        name='draft-post-update'
    ),
    path('post/preview/<slug:slug>/', views.preview, name='post-preview'),
    re_path(r'post/'+ymds_re+'$',
            views.PostDetailView.as_view(), name='post-detail'),
    re_path(r'post/'+ymds_re+'update/$',
            views.PostUpdateView.as_view(), name='post-update'),
    re_path(r'post/'+ymds_re+'delete/$',
            views.PostDeleteView.as_view(), name='post-delete'),
    path('post/recommended-posts/', views.get_recommended_posts,
         name='recommended-posts'),
    path('post/bookmark/', views.bookmark_post, name='bookmark-post'),
    path('post/tag/', views.get_tags, name='all-tags'),
    path('post/tag/<slug:slug>/', views.TaggedPostListView.as_view(), name='tagged'),
    path('post/featured-posts/',
         views.FeaturedPostListView.as_view(), name='featured-posts'),
    path('post/latest-posts/', views.get_latest_posts, name='latest-posts'),
    path('post/trending-posts/', views.get_trending_posts, name='trending-posts'),
    path('post/category/', views.get_category, name='all-categories'),
    path('post/category/<slug:slug>/',
         views.CategoryPostListView.as_view(), name='categorised'),
    re_path(r'post/'+ymd_re+'$', views.get_timewise_list, name='timewise-list'),
]
