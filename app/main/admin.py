from django.contrib import admin
from main.models import Product, Order, Article, Material, Contacts, Review
from django.utils.html import format_html
from django import forms



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'comment')   


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'created_at', 'updated_at', 'image_preview')
    list_filter = ('status', 'author', 'created_at')
    search_fields = ('title', 'content', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'author', 'status')
        }),
        ('Содержание', {
            'fields': ('short_description', 'content')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.image.url)
        return "Нет изображения"
    image_preview.short_description = 'Превью'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Если это новая статья
            obj.author = request.user
        super().save_model(request, obj, form, change)

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = Material.objects.all().order_by('name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'material', 'price')
    list_filter = ('category', 'material')
    search_fields = ('name', 'description')

admin.site.register(Material, MaterialAdmin)

@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('address','phone')
    list_filter = ('address', 'phone')
    search_fields = ('address', 'phone')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user', 'created_at')