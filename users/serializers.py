from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


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
            'pix_key'
        )
    


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_type = serializers.ChoiceField(
        choices=User.Perfil.choices,
        required=False,
        default=User.Perfil.BARBER.value
    )
    city = serializers.CharField(source='get_city_display', read_only=True)
    raw_city = serializers.ChoiceField(
        choices=User.Cidade.choices,
        write_only=True,
        required=False,
        source='city'
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
            'raw_city',
            'whatsapp',
            'avatar',
            'pix_key'
        )

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            profile_type=validated_data.get(
                'profile_type', User.Perfil.BARBER.value),
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
