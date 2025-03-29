from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Perfil(models.TextChoices):
        BARBER = 'barbeiro', 'barbeiro'
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
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço")

    # Email será usado para login, não o username
    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Rating(models.Model):
    barber = models.ForeignKey(User, on_delete=models.CASCADE,related_name='received_ratings', verbose_name='Barbeiro')
    client = models.ForeignKey(User, on_delete=models.CASCADE,related_name='given_ratings', verbose_name='Cliente')
    rating = models.PositiveIntegerField(verbose_name='Avaliação', choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')

    class Meta:
        unique_together = ['barber', 'client']

    def __str__(self):
        return f'Avaliação de {self.client.email} para {self.barber.email}'

    def save(self, *args, **kwargs):
        if self.client.profile_type != User.Perfil.CLIENT:
            raise ValueError('Apenas clientes podem fazer avaliações')
        if self.barber.profile_type != User.Perfil.BARBER:
            raise ValueError('Apenas barbeiros podem ser avaliados')

        super().save(*args, **kwargs)

    @staticmethod
    def get_average_rating(barber):
        """
        Retorna a média de avaliações de um barbeiro
        O valor retornado será entre 0 e 5
        """
        ratings = Rating.objects.filter(barber=barber)
        if not ratings.exists():
            return 0.00

        average = ratings.aggregate(models.Avg('rating'))['rating__avg']
        return round(average, 2)
