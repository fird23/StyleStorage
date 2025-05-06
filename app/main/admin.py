from django.contrib import admin
from .models import Product, Order

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'material')
    search_fields = ('name', 'description')
    list_filter = ('category', 'material')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'comment')   