from django.contrib import admin
from django.urls import path
from . import views

app_name = 'Blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
]

