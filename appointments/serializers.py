from rest_framework import serializers

from services.models import Services
from .models import Appointment
from users.models import User
from users.serializers import UserSerializer
from schedule.models import TimeSlot
from schedule.serializers import TimeSlotSerializer
from services.serializers import ServicoSerializer


class AppointmentSerializer(serializers.ModelSerializer):
    barber = UserSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    service = ServicoSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)

    barber_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='barber', write_only=True
    )
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='client', write_only=True
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Services.objects.all(), source='service', write_only=True
    )
    time_slot_id = serializers.PrimaryKeyRelatedField(
        queryset=TimeSlot.objects.all(), source='time_slot', write_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "barber", "barber_id",
            "client", "client_id",
            "service", "service_id",
            "time_slot", "time_slot_id",
            "status",
            "price",
            "is_free",
            "created_at",
        ]
        read_only_fields = ["id", "is_free", "created_at"]

    def create(self, validated_data):
        service = validated_data['service']
        validated_data['price'] = service.price
        return Appointment.objects.create(**validated_data)
