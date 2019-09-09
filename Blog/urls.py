from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Users import views as user_views
from . import views

app_name = 'Blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='Users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='Users/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    ]

