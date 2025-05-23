from django.db import models
from .user import CustomUser
from .product import Product
from .payment import PaymentCard
from django.dispatch import receiver

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В обработке'),
        ('completed', 'Завершен'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    payment_card = models.ForeignKey(PaymentCard, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_address = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Заказ #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Заказ #{self.order.id})"
    
class Meta:
    verbose_name = 'Заказы'
    verbose_name_plural = 'Заказы'
    ordering = ['name']
