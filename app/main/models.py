from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import json

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.JSONField(default=dict, blank=True)
    bonus_points = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if self.phone:
            digits = ''.join(filter(str.isdigit, self.phone))
            if digits.startswith('8'):
                digits = '7' + digits[1:]
            if digits.startswith('9'):
                digits = '7' + digits
            self.phone = f'+7{digits[1:11]}'
        super().save(*args, **kwargs)
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            return '+' + ''.join(filter(str.isdigit, phone))[1:11]
        return phone

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('wardrobe', 'Шкафы-купе'),
        ('closet', 'Гардеробные системы'),
    ]

    MATERIAL_CHOICES = [
        ('ДСП', 'ДСП'),
        ('МДФ', 'МДФ'),
        ('Натуральное дерево', 'Натуральное дерево'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES)
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
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"Заказ #{self.id}"

class PaymentCard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_cards')
    card_number = models.CharField(max_length=19)
    expiry_date = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Карта {self.card_number[-4:]} пользователя {self.user.username}"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} в корзине {self.cart.user.username}"
