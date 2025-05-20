from django.db import models

class Material(models.Model):
    name = models.CharField('Название материала', max_length=100, unique=True)
    description = models.TextField('Описание', blank=True)
    
    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['name']
    
    def __str__(self):
        return self.name