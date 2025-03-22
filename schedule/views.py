from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from core.permissions import IsBarber
from schedule.models import TimeSlot, WorkDay
from schedule.serializers import TimeSlotSerializer, WorkDaySerializer
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class WorkDayListCreateView(APIView):
    """
    Lista todos os WorkDays ou cria um novo.
    """
    
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Lista todos os Dias de trabalho ativos do barbeiro autenticado.",
        responses={
            200: "Sucesso",
            401: "Não autorizado",
        }
    )
    def get(self, request):
        work_day = WorkDay.objects.filter(barber=request.user, is_active=True)
        serializer = WorkDaySerializer(work_day, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Cria um novo dia de trabalho para o barbeiro autenticado.",
        request_body=WorkDaySerializer,
        responses={
            201: "Criado com sucesso",
            401: "Não autorizado",
        }
    )
    def post(self, request):
        serializer = WorkDaySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(barber=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkDayDetailAPIView(APIView):
    """
    Recupera, atualiza ou deleta um WorkDay específico.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    def get_object(self, pk):
        try:
            return WorkDay.objects.get(barber=self.request.user, pk=pk, is_active=True)
        except WorkDay.DoesNotExist:
            raise NotFound(detail="Dia de trabalho não encontrado")

    @swagger_auto_schema(
        operation_description="Recupera os detalhes de um dia de trabalho específico.",
        responses={
            200: WorkDaySerializer,
            404: "Dia de trabalho não encontrado",
        }
    )
    def get(self, request, pk):
        work_day = self.get_object(pk)
        serializer = WorkDaySerializer(work_day)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Atualiza os dados de um dia de trabalho específico.",
        request_body=WorkDaySerializer,
        responses={
            200: WorkDaySerializer,
            400: "Erro de validação",
            401: "Erro de permissão"
        }
    )
    def put(self, request, pk):
        work_day = self.get_object(pk)
        serializer = WorkDaySerializer(work_day, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Desativa um WorkDay específico.",
        responses={
            204: "Dia de trabalho desativado com sucesso",
        }
    )
    def delete(self, request, pk):
        work_day = self.get_object(pk)
        work_day.is_active = False
        work_day.time_slots.update(is_active=False, is_available=False)
        work_day.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkDayPublicListView(APIView):
    """
    Lista todos os work_days rota pública
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Lista todos os dias de trabalho de um barbeiro específico pública.",
        manual_parameters=[
            openapi.Parameter(
                'barber_id', openapi.IN_QUERY, description="ID do barbeiro", type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: WorkDaySerializer(many=True),
            404: "Barbeiro não encontrado",
        }
    )
    def get(self, request):
        barber_id = request.query_params.get('barber_id')
        work_day = WorkDay.objects.filter(barber_id=barber_id, is_active=True)
        serializer = WorkDaySerializer(work_day, many=True)
        return Response(serializer.data)


class GenerateSlotsView(APIView):
    """
    Gera os horários disponíveis (slots) para um  dia de trabalho (work_day)
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Gera os horários disponíveis (slots) para um dia de trabalho específico.",
        request_body=None,
        responses={
            201: openapi.Response(
                description="Horários gerados com sucesso.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de sucesso."),
                        'slots': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            ),
            404: "WorkDay não encontrado ou inativo.",
            401: "Não autorizado",
        }
    )
    def post(self, request, work_day_id):
        try:
            print(request.user)
            work_day = WorkDay.objects.get(id=work_day_id, barber=request.user, is_active=True)
        except WorkDay.DoesNotExist:
            raise NotFound(detail="WorkDay não encontrado ou inativo.")

        slots = work_day.generate_time_slots()
        serializer = TimeSlotSerializer(slots, many=True)
        return Response(
            {"message": "Horários gerados com sucesso.", "slots": serializer.data},
            status=status.HTTP_201_CREATED
        )
    

class DeleteSlotsView(APIView):
    """
    Deleta todos os horários (slots) para um dia de trabalho (work_day).
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Deleta todos os horários (slots) para um dia de trabalho específico.",
        request_body=None,
        responses={
            200: openapi.Response(
                description="Todos os horários foram deletados com sucesso.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de sucesso.")
                    }
                )
            ),
            404: "WorkDay não encontrado ou inativo.",
            401: "Não autorizado",
        }
    )
    def delete(self, request, work_day_id):
        try:
            work_day = WorkDay.objects.get(id=work_day_id, barber=request.user, is_active=True)
        except WorkDay.DoesNotExist:
            raise NotFound(detail="WorkDay não encontrado ou inativo.")

        time_slots = TimeSlot.objects.filter(work_day=work_day)
        time_slots.delete()

        return Response(
            {"message": "Todos os horários foram deletados com sucesso."},
            status=status.HTTP_200_OK
        )


class AvailableTimeSlotsView(APIView):
    """
    Retorna os horários disponíveis para um determinado dia de trabalho (`WorkDay`).
    """

    @swagger_auto_schema(
        operation_description="Retorna os horários disponíveis para um determinado dia de trabalho (WorkDay).",
        request_body=None,
        responses={
            200: openapi.Response(
                description="Lista de horários disponíveis para o dia de trabalho.",
                schema=TimeSlotSerializer(many=True)
            ),
            404: openapi.Response(
                description="WorkDay não encontrado ou não está ativo.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro.")
                    }
                )
            ),
        }
    )
    def get(self, request, work_day_id):
        try:
            work_day = WorkDay.objects.get(id=work_day_id, is_active=True)
        except WorkDay.DoesNotExist:
            return Response({"error": "WorkDay não encontrado"}, status=404)
        available_slots = TimeSlot.objects.filter(work_day=work_day, is_available=True, is_active=True)
        serializer = TimeSlotSerializer(available_slots, many=True)
        return Response(serializer.data)


class DeleteTimeSlotView(APIView):
    """
    Deleta um único horário pelo ID.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    @swagger_auto_schema(
        operation_description="Deleta um único horário (TimeSlot) pelo ID.",
        request_body=None,
        responses={
            204: openapi.Response(
                description="Horário excluído com sucesso."
            ),
            404: openapi.Response(
                description="Horário não encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Mensagem de erro.")
                    }
                )
            ),
        }
    )
    def delete(self, request, time_slot_id):
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            time_slot.delete()
            return Response({"message": "Horário excluído com sucesso"}, status=status.HTTP_204_NO_CONTENT)
        except TimeSlot.DoesNotExist:
            return Response({"error": "Horário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
