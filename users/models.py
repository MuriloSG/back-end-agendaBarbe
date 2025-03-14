from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Perfil(models.TextChoices):
        BARBER = 'barbeiro', 'Barbeiro'
        CLIENT = 'cliente', 'cliente'

    class Cidade(models.TextChoices):
        SALINAS_MG = 'salinas_mg', 'Salinas'
        
    email = models.EmailField(unique=True)
    profile_type = models.CharField(choices=Perfil.choices, verbose_name='Perfil', default=Perfil.BARBER.value, max_length=16)
    is_active = models.BooleanField(verbose_name='ativo', default=True)
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)

    whatsapp = models.CharField(max_length=20, blank=True, null=True, verbose_name="WhatsApp")
    avatar = models.CharField(max_length=255, blank=True, null=True, verbose_name="Avatar")
    pix_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave Pix")
    city = models.CharField(max_length=20, choices=Cidade.choices,blank=True,null=True,verbose_name="Cidade")
    confirmed_appointments_count = models.PositiveIntegerField(default=0, verbose_name="Agendamentos Confirmados para recompensa")

    # Email será usado para login, não o username
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
