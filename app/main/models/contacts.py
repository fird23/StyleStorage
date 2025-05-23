from django.db import models

class Contacts(models.Model):

    address = models.CharField(
        max_length=255,
        help_text="Например: ул. Примерная, 10"
    )
    
    working_hours = models.CharField(
        max_length=50,
        help_text="Например: 10:00-20:00"
    )
    
    phone = models.CharField(
        max_length=20,
        help_text="Например: +7 951 123-45-67"
    )
    
    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'
        ordering = ['address']

    def __str__(self):
        return f"{self.address} ({self.working_hours})"