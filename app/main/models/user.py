from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

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