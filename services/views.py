from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from core.permissions import IsBarber
from core.utils.upload_images_firebase import upload_services_to_supabase
from .models import Services
from .serializers import ServicoSerializer
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser


class ServicoListCreateView(APIView):
    """
    Lista todos os Serviços de um barbeiro ou cria um novo.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Lista todos os serviços de um barbeiro autenticado.",
        responses={
            200: openapi.Response(
                description="Lista de serviços do barbeiro",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'description': openapi.Schema(type=openapi.TYPE_STRING),
                        'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    })
                )
            ),
            401: "Não autorizado",
        }
    )
    def get(self, request):
        servicos = Services.objects.filter(barber=request.user, is_active=True)
        serializer = ServicoSerializer(servicos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Cria um novo serviço para o barbeiro autenticado.",
        request_body=ServicoSerializer,
        responses={
            201: "Serviço criado com sucesso.",
            400: "Erro de validação, dados inválidos.",
        }
    )
    def post(self, request):
        image_file = request.FILES.get('service_img')
        if image_file:
            avatar_url = upload_services_to_supabase(image_file, image_file.name)
            request.data['image'] = avatar_url
        serializer = ServicoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(barber=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServicoDetailView(APIView):
    """
    Recupera, atualiza ou deleta um serviço específico.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    def get_object(self, pk):
        try:
            return Services.objects.get(pk=pk, barber=self.request.user, is_active=True)
        except Services.DoesNotExist:
            raise NotFound(detail="Serviço não encontrado")

    @swagger_auto_schema(
        operation_description="Recupera um serviço específico do barbeiro autenticado.",
        responses={
            200: ServicoSerializer,
            404: "Serviço não encontrado.",
        }
    )
    def get(self, request, pk):
        servico = self.get_object(pk)
        serializer = ServicoSerializer(servico)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Atualiza um serviço específico com base no `pk`.",
        request_body=ServicoSerializer,
        responses={
            200: ServicoSerializer,
            400: "Erro de validação, dados inválidos.",
        }
    )
    def put(self, request, pk):
        servico = self.get_object(pk)
        serializer = ServicoSerializer(servico, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Atualiza parcialmente um serviço específico (dados opcionais).",
        request_body=ServicoSerializer,
        responses={
            200: ServicoSerializer,
            400: "Erro de validação, dados inválidos.",
        }
    )
    def patch(self, request, pk):
        servico = self.get_object(pk)
        serializer = ServicoSerializer(servico, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_description="Desativa um serviço específico.",
        responses={
            204: "Serviço desativado com sucesso.",
        }
    )
    def delete(self, request, pk):
        servico = self.get_object(pk)
        servico.is_active = False
        servico.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServicoPublicListView(APIView):
    """
    Lista todos os Serviços rota pública
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Lista todos os serviços ativos de um barbeiro específico, baseado no `barber_id`.",
        manual_parameters=[
            openapi.Parameter('barber_id', openapi.IN_QUERY, description="ID do barbeiro cujos serviços serão listados", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: ServicoSerializer(many=True),
            400: "Erro ao processar a solicitação.",
        }
    )
    def get(self, request):
        barber_id = request.query_params.get('barber_id')
        servicos = Services.objects.filter(barber_id=barber_id, is_active=True)
        serializer = ServicoSerializer(servicos, many=True)
        return Response(serializer.data)
