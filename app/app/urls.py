# app/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('catalog/', views.catalog, name='catalog'),
    path('order/', views.order, name='order'),
    path('contacts/', views.contacts, name='contacts'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]