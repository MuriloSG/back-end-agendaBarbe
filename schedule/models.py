from django.db import models
from users.models import User
from datetime import datetime, timedelta, time


class WorkDay(models.Model):
    class Weekday(models.TextChoices):
        MONDAY = 'monday', 'Segunda-feira'
        TUESDAY = 'tuesday', 'Terça-feira'
        WEDNESDAY = 'wednesday', 'Quarta-feira'
        THURSDAY = 'thursday', 'Quinta-feira'
        FRIDAY = 'friday', 'Sexta-feira'
        SATURDAY = 'saturday', 'Sábado'
        SUNDAY = 'sunday', 'Domingo'

    WEEKDAY_ORDER = {
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6,
        'sunday': 7
    }

    barber = models.ForeignKey(User, related_name="barber_dias_de_trabalho", on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=Weekday.choices, null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Ativo', default=True)

    start_time = models.TimeField(help_text="Hora de início do expediente", null=True, blank=True)
    end_time = models.TimeField(help_text="Hora de fim do expediente", null=True, blank=True)

    lunch_start_time = models.TimeField(help_text="Hora de início do almoço", null=True, blank=True)
    lunch_end_time = models.TimeField(help_text="Hora de fim do almoço", null=True, blank=True)
    slot_duration = models.PositiveIntegerField(default=30, help_text="Duração de cada horário em minutos")
    weekday_order = models.PositiveSmallIntegerField(default=8, editable=False)

    def __str__(self):
        return f'{self.barber} - {self.get_day_of_week_display()}'

    class Meta:
        ordering = ['is_active', 'weekday_order']
        indexes = [
            models.Index(
                fields=['barber', 'is_active'],
                name='barber_active_idx'
            ),
        ]

    def get_weekday_order(self):
        return self.WEEKDAY_ORDER.get(self.day_of_week, 8)
    
    def generate_time_slots(self):
        """
        Gera os horários baseados nos horários de início, fim e almoço definidos para o dia
        """

        if isinstance(self.start_time, str):
            self.start_time = time.fromisoformat(self.start_time)
        if isinstance(self.lunch_start_time, str):
            self.lunch_start_time = time.fromisoformat(self.lunch_start_time)
        if isinstance(self.lunch_end_time, str):
            self.lunch_end_time = time.fromisoformat(self.lunch_end_time)
        if isinstance(self.end_time, str):
            self.end_time = time.fromisoformat(self.end_time)

        # Apaga(desativa) os horários antigos para evitar duplicação
        TimeSlot.objects.filter(work_day=self).update(is_active=False, is_available=False)

        slots = []
        slot_duration = self.slot_duration
        current_time = self.start_time  
        end_of_work = self.end_time

        while current_time < self.lunch_start_time:
            slots.append(TimeSlot(work_day=self, time=current_time, is_available=True))
            current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=slot_duration)).time()

        current_time = self.lunch_end_time
        while current_time < end_of_work:
            slots.append(TimeSlot(work_day=self, time=current_time, is_available=True))
            current_time = (datetime.combine(datetime.today(), current_time) + timedelta(minutes=slot_duration)).time()

        if slots:
            TimeSlot.objects.bulk_create(slots)

        return slots
    
    def save(self, *args, **kwargs):
        self.weekday_order = self.WEEKDAY_ORDER.get(self.day_of_week, 8)
        super().save(*args, **kwargs)
        if self and self.is_active or self.pk:
            self.generate_time_slots()


class TimeSlot(models.Model):
    work_day = models.ForeignKey(WorkDay, on_delete=models.CASCADE, related_name='time_slots')
    time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["time"]

    def __str__(self):
        return f"{self.work_day} - {self.time}"


