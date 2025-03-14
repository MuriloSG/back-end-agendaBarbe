from django.db import models
from users.models import User
from services.models import Services
from schedule.models import TimeSlot

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        CONFIRMED = 'confirmed', 'Confirmado'
        CANCELED = 'canceled', 'Cancelado'

    barber = models.ForeignKey(User, on_delete=models.CASCADE, related_name="barber_appointments")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_appointments")
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ 
        Atualiza o contador de agendamentos confirmados no cliente e aplica a recompensa a cada 5 agendamentos. 
        """
        previous_status = None

        if self.pk: 
            previous_status = Appointment.objects.get(pk=self.pk).status

        if not self.is_free:
            confirmed_appointments = Appointment.objects.filter(
                client=self.client,
                status=self.Status.CONFIRMED,
                is_free=False 
            ).count()

            if confirmed_appointments > 0 and confirmed_appointments % 5 == 0:
                self.is_free = True
                self.price = 0 

        super().save(*args, **kwargs)

        # Atualiza o contador de agendamentos confirmados no usuário
        if self.status == self.Status.CONFIRMED and previous_status != self.Status.CONFIRMED:
            self.client.confirmed_appointments_count += 1
            self.client.save()

        elif previous_status == self.Status.CONFIRMED and self.status != self.Status.CONFIRMED:
            self.client.confirmed_appointments_count = max(0, self.client.confirmed_appointments_count - 1)
            self.client.save()

    def __str__(self):
        return f"{self.client} - {self.service} em {self.time_slot.time}"
