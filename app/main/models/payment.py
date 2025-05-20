from django.db import models
from .user import CustomUser

class PaymentCard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_cards')
    card_number = models.CharField(max_length=19)
    expiry_date = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Карта {self.card_number[-4:]} пользователя {self.user.username}"