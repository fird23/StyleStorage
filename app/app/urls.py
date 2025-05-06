from main import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from main.views import CustomLoginView
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('catalog/', views.catalog, name='catalog'),
    path('order/', views.order, name='order'),
    path('contacts/', views.contacts, name='contacts'),
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_card/<int:card_id>/', views.delete_card, name='delete_card'),
    path('delete_address/<int:index>/', views.delete_address, name='delete_address'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)