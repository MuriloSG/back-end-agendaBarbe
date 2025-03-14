from django.db import models
from django.core.validators import MinValueValidator

from users.models import User

class Services(models.Model):
    barber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_barber')
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    created_by = models.DateTimeField(auto_now_add=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True, verbose_name="Imagens")

    def __str__(self):
        return self.name