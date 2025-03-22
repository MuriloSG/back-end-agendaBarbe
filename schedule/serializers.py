from rest_framework import serializers

from users.serializers import UserSerializer
from .models import TimeSlot, WorkDay


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", "work_day", "time", "is_available"]


class WorkDaySerializer(serializers.ModelSerializer):
    time_slots = serializers.SerializerMethodField()
    barber = UserSerializer(read_only=True)
    day_of_week_display = serializers.SerializerMethodField()
    free_time_count = serializers.SerializerMethodField()
    busy_time_count = serializers.SerializerMethodField()

    class Meta:
        model = WorkDay
        fields = [
            'id', 'barber', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time',
            'lunch_start_time', 'lunch_end_time', 'slot_duration', 'free_time_count', 'busy_time_count', 'time_slots'
        ]

    def get_time_slots(self, obj):
        """Filtra slots ativos e serializa"""
        active_slots = obj.time_slots.filter(is_active=True)
        return TimeSlotSerializer(active_slots, many=True).data

    def validate(self, data):
        barber = self.context['request'].user
        day_of_week = data.get('day_of_week')
        if day_of_week:
            queryset = WorkDay.objects.filter(barber=barber, day_of_week=day_of_week)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError({
                    'day_of_week': 'Você já possui um horário registrado para este dia da semana.'
                })

        return data
    
    def get_day_of_week_display(self, obj):
        DIAS_DA_SEMANA = {
            'sunday': 'Domingo',
            'monday': 'Segunda-feira',
            'tuesday': 'Terça-feira',
            'wednesday': 'Quarta-feira',
            'thursday': 'Quinta-feira',
            'friday': 'Sexta-feira',
            'saturday': 'Sábado',
        }
        return DIAS_DA_SEMANA.get(obj.day_of_week, obj.day_of_week)

    def get_free_time_count(self, obj):
        return obj.time_slots.filter(is_available=True, is_active=True).count()

    def get_busy_time_count(self, obj):
        return obj.time_slots.filter(is_available=False, is_active=True).count()

