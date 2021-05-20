from ckeditor_uploader import views as ck_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.decorators.cache import never_cache
from django.views.decorators.http import condition

from post.decorators.restrict_access import require_group, require_superuser
from post.models import Post
from post.views import LatestPostRSSFeed as rss_feed
from user_profile import views as user_views


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
    path('', include('post.urls')),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            redirect_authenticated_user=True,
            template_name='user_profile/login.html'
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='user_profile/logout.html'),
        name='logout',
    ),
    path('password-change/', user_views.password_change, name='password-change'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='user_profile/password_reset.html'),
         name='password_reset'
         ),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user_profile/password_reset_done.html'),
         name='password_reset_done'
         ),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='user_profile/password_reset_confirm.html'),
         name='password_reset_confirm'
         ),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user_profile/password_reset_complete.html'),
         name='password_reset_complete'
         ),
    path('latest/feed',
         condition(last_modified_func=Post.objects.latest_entry)(rss_feed()),
         name='rss-feed'
         ),
    path('privacy-policy', user_views.privacy_policy, name='privacy-policy'),
    path('image-license', user_views.image_license, name='image-license'),
]

# Adds ckeditor urls
urlpatterns += [
    path('ckeditor/upload/', require_group('editor')
         (ck_views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(require_group('editor')(ck_views.browse)),
         name='ckeditor_browse'),
]

# Adds third-party urls urls
urlpatterns += [
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path('comment/', include('comment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
