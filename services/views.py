from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from core.permissions import IsBarber
from .models import Services
from .serializers import ServicoSerializer
from rest_framework.exceptions import NotFound



class ServicoListCreateView(APIView):
    """
    Lista todos os Serviços de um barbeiro ou cria um novo.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    def get(self, request):
        servicos = Services.objects.filter(barber=request.user, is_active=True)
        serializer = ServicoSerializer(servicos, many=True)
        return Response(serializer.data)

    def post(self, request):
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

    def get(self, request, pk):
        servico = self.get_object(pk)
        serializer = ServicoSerializer(servico)
        return Response(serializer.data)

    def put(self, request, pk):
        servico = self.get_object(pk)
        serializer = ServicoSerializer(servico, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        servico = self.get_object(pk)
        serializer = ServicoSerializer(servico, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def get(self, request):
        barber_id = request.query_params.get('barber_id')
        servicos = Services.objects.filter(barber_id=barber_id, is_active=True)
        serializer = ServicoSerializer(servicos, many=True)
        return Response(serializer.data)
