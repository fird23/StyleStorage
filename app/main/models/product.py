from django.db import models
from .material import Material  # Импорт из того же каталога

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('wardrobe', 'Шкафы-купе'),
        ('closet', 'Гардеробные системы'),
    ]
    
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    category = models.CharField(
        'Категория',
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Материал'
    )
    dimensions = models.CharField('Размеры', max_length=50)
    image = models.ImageField('Изображение', upload_to='products/')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name