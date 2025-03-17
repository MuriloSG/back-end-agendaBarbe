from rest_framework import serializers

from users.backends import User
from .models import Services
from users.serializers import UserSerializer


class ServicoSerializer(serializers.ModelSerializer):
    barber = UserSerializer(read_only=True)

    class Meta:
        model = Services
        fields = [
            'id',
            'name',
            'description',
            'price',
            'image',
            'barber',
        ]
        read_only_fields = ['barber', 'created_by']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("O preço deve ser maior que zero")
        return value

