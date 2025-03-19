from rest_framework import serializers

from users.serializers import UserSerializer
from .models import TimeSlot, WorkDay


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", "work_day", "time", "is_available"]


class WorkDaySerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)
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
        return obj.time_slots.filter(is_available=True).count()

    def get_busy_time_count(self, obj):
        return obj.time_slots.filter(is_available=False).count()

