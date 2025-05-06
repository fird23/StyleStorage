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
            # Нормализация номера
            digits = ''.join(filter(str.isdigit, self.phone))
            if digits.startswith('8'):
                digits = '7' + digits[1:]
            if digits.startswith('9'):
                digits = '7' + digits
            self.phone = f'+7{digits[1:11]}'  # Всегда 11 цифр
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

