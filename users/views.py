from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings

from core.utils.upload_images_firebase import upload_avatar_to_supabase
from users.models import User, Rating
from users.serializers import (
    UserLoginSerializer, 
    UserRegistrationSerializer, 
    UserSerializer, 
    RatingSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class UserRegistrationView(APIView):
    """Registra um novo usuário e cria um token de autenticação."""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Registra um novo usuário e retorna as informações do usuário junto com o token de autenticação.",
        request_body=UserRegistrationSerializer,
        responses={
            201: "Usuário registrado com sucesso.",
            400: "Erro na validação dos dados enviados.",
        }
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            Token.objects.create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': user.auth_token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """Realiza o login de um usuário e retorna o token de autenticação."""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Realiza o login de um usuário e retorna um token de autenticação.",
        request_body=UserLoginSerializer,
        responses={
            200: "Login bem-sucedido. Retorna o token e os dados do usuário.",
            401: "Credenciais inválidas.",
        }
    )
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """Realiza o logout de um usuário, excluindo o token de autenticação."""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Realiza o logout do usuário, excluindo o token de autenticação.",
        responses={
        }
    )
    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            {'detail': 'Logout realizado com sucesso.'},
            status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    """
    Ver, deletar e atualiza o perfil do usuário autenticado.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Recupera o perfil do usuário autenticado.",
        responses={
            200: "Perfil do usuário recuperado com sucesso.",
            401: "Não autorizado. O usuário precisa estar autenticado.",
        }
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Atualiza o perfil do usuário autenticado, incluindo a imagem de avatar.",
        responses={
            200: "Perfil do usuário atualizado com sucesso.",
            401: "Não autorizado. O usuário precisa estar autenticado.",
        },
        request_body=UserSerializer
    )
    def patch(self, request):
        image_file = request.FILES.get('avatar_file')
        if image_file:
            avatar_url = upload_avatar_to_supabase(image_file, image_file.name)
            request.data['avatar'] = avatar_url
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Desativa o perfil do usuário autenticado.",
        responses={
            204: "Perfil do usuário deletado com sucesso.",
            401: "Não autorizado. O usuário precisa estar autenticado.",
        }
    )
    def delete(self, request):
        user = request.user
        user.is_active = False 
        user.save(update_fields=["is_active"])
        return Response({'detail': 'Perfil deletado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)


class BarberListView(APIView):
    """
    Lista apenas os usuários do tipo barbeiro da cidade do cliente.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Recupera barbeiros filtrados por cidade e nome",
        manual_parameters=[
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Filtrar por nome do barbeiro (busca parcial)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: UserSerializer(many=True),
            401: "Não autorizado",
            400: "Parâmetros inválidos"
        }
    )
    def get(self, request):
        barbers = User.objects.filter(profile_type=User.Perfil.BARBER, is_active=True, city=request.user.city)
        name_filter = request.query_params.get('name', '')
        if name_filter:
            barbers = barbers.filter(username__icontains=name_filter)
        serializer = UserSerializer(barbers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cria uma nova avaliação para um barbeiro",
        request_body=RatingSerializer,
        responses={
            201: "Avaliação criada com sucesso",
            400: "Dados inválidos ou usuário não é um cliente",
            404: "Barbeiro não encontrado"
        }
    )
    def post(self, request):
        # Verifica se o usuário é um cliente
        if request.user.profile_type != User.Perfil.CLIENT:
            return Response(
                {'error': 'Apenas clientes podem fazer avaliações'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RatingSerializer(data=request.data)
        if serializer.is_valid():
            # Verifica se o barbeiro existe e é ativo
            try:
                barber = User.objects.get(
                    id=serializer.validated_data['barber_id'],
                    profile_type=User.Perfil.BARBER,
                    is_active=True
                )
            except User.DoesNotExist:
                return Response(
                    {'error': 'Barbeiro não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Verifica se o cliente já avaliou este barbeiro
            if Rating.objects.filter(barber=barber, client=request.user).exists():
                return Response(
                    {'error': 'Você já avaliou este barbeiro'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Cria a avaliação
            rating = Rating.objects.create(
                barber=barber,
                client=request.user,
                rating=serializer.validated_data['rating']
            )

            return Response(
                RatingSerializer(rating).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Envia um email com o link para redefinição de senha.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Envia um email com link para redefinição de senha",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: "Email enviado com sucesso",
            400: "Email não encontrado ou inválido",
            500: "Erro ao enviar email"
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # Gera o token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Cria o link de reset
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
                
                # Envia o email
                subject = 'Recuperação de Senha - Agenda Barbe'
                message = f'''
                Olá {user.username},
                
                Você solicitou a recuperação de senha. Clique no link abaixo para redefinir sua senha:
                
                {reset_url}
                
                Se você não solicitou esta recuperação, ignore este email.
                
                Atenciosamente,
                Equipe Agenda Barbe
                '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({
                    'detail': 'Email de recuperação enviado com sucesso.'
                })
                
            except User.DoesNotExist:
                return Response({
                    'detail': 'Usuário não encontrado.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirma a redefinição de senha usando o token enviado por email.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Confirma a redefinição de senha",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: "Senha alterada com sucesso",
            400: "Token inválido ou expirado",
            404: "Usuário não encontrado"
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid)
                
                if default_token_generator.check_token(user, serializer.validated_data['token']):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({
                        'detail': 'Senha alterada com sucesso.'
                    })
                else:
                    return Response({
                        'detail': 'Token inválido ou expirado.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'detail': 'Link de recuperação inválido.'
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

