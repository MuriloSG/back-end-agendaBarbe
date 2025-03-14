from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser

from core.utils.upload_images_firebase import upload_avatar_to_supabase
from users.models import User
from users.serializers import UserLoginSerializer, UserRegistrationSerializer, UserSerializer


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.IsAuthenticated]

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

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        image_file = request.FILES.get('avatar_file')
        if image_file:
            avatar_url = upload_avatar_to_supabase(image_file, image_file.name)
            print(avatar_url)
            request.data['avatar'] = avatar_url
        print(image_file)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        user.is_active = False 
        user.save(update_fields=["is_active"])
        return Response({'detail': 'Perfil deletado com sucesso.'}, status=status.HTTP_204_NO_CONTENT)


class BarberListView(APIView):
    """
    Lista apenas os usuários do tipo barbeiro.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        barbers = User.objects.filter(profile_type=User.Perfil.BARBER, is_active=True, city=request.user.city)
        serializer = UserSerializer(barbers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

