"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import absolute_import
from django.contrib import admin
from ckeditor_uploader import views as ck_views
from django.views.decorators.cache import never_cache
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from Users import views as user_views
from Blog.views import LatestPostRSSFeed as rss_feed
from Blog.decorators.restrict_access import group, require_superuser
import debug_toolbar
from django.views.decorators.http import condition
from Blog.manager import latest_entry


def dec_patterns(patterns):
    decorated_patterns = []
    for pattern in patterns:
        callback = pattern.callback
        pattern.callback = require_superuser(callback)
        pattern._callback = require_superuser(callback)
        decorated_patterns.append(pattern)
    return decorated_patterns


url_patterns_admin = [
    path('admin/', (dec_patterns(admin.site.urls[0]),) + admin.site.urls[1:]),
]

urlpatterns = url_patterns_admin + [
    # path('admin/', admin.site.urls),
    path('', include('Blog.urls')),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='Users/login.html'),
         name='login'
         ),
    path('logout/', auth_views.LogoutView.as_view(
        template_name='Users/logout.html'),
        name='logout'
    ),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='Users/password_reset.html'),
         name='password_reset'
         ),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='Users/password_reset_done.html'),
         name='password_reset_done'
         ),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='Users/password_reset_confirm.html'),
         name='password_reset_confirm'
         ),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='Users/password_reset_complete.html'),
         name='password_reset_complete'
         ),
    path('latest/feed',
         condition(last_modified_func=latest_entry)(rss_feed()),
         name='rss-feed'
         ),
]

# Adds ckeditor urls
# urlpatterns += [path('ckeditor/', include('ckeditor_uploader.urls'))]
urlpatterns += [
    path('ckeditor/upload/', group('editor')
         (ck_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(group('editor')(ck_views.browse)),
         name='ckeditor_browse'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

    urlpatterns += [path('__debug__', include(debug_toolbar.urls))]
