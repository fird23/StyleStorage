from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('wardrobe', 'Шкафы-купе'),
        ('closet', 'Гардеробные системы'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    material = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('completed', 'Завершен'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"Заказ #{self.id}"

