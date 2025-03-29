from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Rating


class UserSerializer(serializers.ModelSerializer):
    profile_type = serializers.CharField(
        source='get_profile_type_display', read_only=True)
    raw_profile_type = serializers.ChoiceField(
        choices=User.Perfil.choices,
        write_only=True,
        required=False,
        source='profile_type'
    )
    city = serializers.CharField(source='get_city_display', read_only=True)
    raw_city = serializers.ChoiceField(
        choices=User.Cidade.choices,
        write_only=True,
        required=False,
        source='city'
    )
    confirmed_appointments_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_type',
            'raw_profile_type',
            'city',
            'raw_city',
            'whatsapp',
            'avatar',
            'pix_key',
            'address',
            'confirmed_appointments_count',
            'average_rating',
            'total_ratings'
        )
        read_only_fields = ('id', 'confirmed_appointments_count')

    def get_average_rating(self, obj):
        if obj.profile_type == User.Perfil.BARBER:
            return Rating.get_average_rating(obj)
        return None

    def get_total_ratings(self, obj):
        if obj.profile_type == User.Perfil.BARBER:
            return Rating.objects.filter(barber=obj).count()
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_type = serializers.ChoiceField(
        choices=User.Perfil.choices,
        required=False,
        default=User.Perfil.BARBER.value
    )
    city = serializers.ChoiceField(
        choices=User.Cidade.choices,
        required=False,
        default=User.Cidade.SALINAS_MG.value
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'profile_type',
            'city',
            'whatsapp',
            'avatar',
            'pix_key',
            'address'
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            profile_type=validated_data.get('profile_type'),
            city=validated_data.get('city'),
            whatsapp= validated_data.get('whatsapp'),
            address= validated_data.get('address'),
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email", write_only=True)
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )

            if not user:
                msg = 'Credenciais inválidas.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Deve incluir "email" e "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class RatingSerializer(serializers.Serializer):
    barber_id = serializers.IntegerField(required=True)
    rating = serializers.IntegerField(required=True, min_value=1, max_value=5)

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('A avaliação deve estar entre 1 e 5')
        return value
