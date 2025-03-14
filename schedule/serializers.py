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
    class Meta:
        model = WorkDay
        fields = ['id', 'barber', 'day_of_week', 'start_time', 'end_time',
                  'lunch_start_time', 'lunch_end_time', 'slot_duration', 'time_slots']



