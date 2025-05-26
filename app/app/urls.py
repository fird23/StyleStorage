from main import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.contrib.sitemaps.views import sitemap
from main.sitemap import ReviewSitemap, StaticSitemap



sitemaps = {
    'reviews': ReviewSitemap,
    'static': StaticSitemap,
}

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
    path('add-product/', views.add_product, name='add_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart_item_quantity/<int:product_id>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('product/<int:product_id>/modal/', views.product_modal, name='product_modal'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('order_detail/', views.OrderDetailView.as_view(), name='order_detail'),
    path('reviews/', views.all_reviews, name='all_reviews'),
    path('reviews/manage/', views.manage_review, name='manage_review'),
    path("robots.txt", RedirectView.as_view(url=staticfiles_storage.url("robots.txt"))),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)