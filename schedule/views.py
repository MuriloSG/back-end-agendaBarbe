from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from core.permissions import IsBarber
from schedule.models import TimeSlot, WorkDay
from schedule.serializers import TimeSlotSerializer, WorkDaySerializer
from rest_framework.exceptions import NotFound


class WorkDayListCreateView(APIView):
    """
    Lista todos os WorkDays ou cria um novo.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]

    def get(self, request):
        work_day = WorkDay.objects.filter(barber=request.user, is_active=True)
        serializer = WorkDaySerializer(work_day, many=True)
        return Response(serializer.data)

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

    def get(self, request, pk):
        work_day = self.get_object(pk)
        serializer = WorkDaySerializer(work_day)
        return Response(serializer.data)

    def put(self, request, pk):
        work_day = self.get_object(pk)
        serializer = WorkDaySerializer(work_day, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        work_day = self.get_object(pk)
        work_day.is_active = False
        work_day.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkDayPublicListView(APIView):
    """
    Lista todos os work_days rota pública
    """
    permission_classes = [permissions.AllowAny]

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

    def get(self, request, work_day_id):
        try:
            work_day = WorkDay.objects.get(id=work_day_id, is_active=True)
        except WorkDay.DoesNotExist:
            return Response({"error": "WorkDay não encontrado"}, status=404)
        available_slots = TimeSlot.objects.filter(work_day=work_day, is_available=True)
        serializer = TimeSlotSerializer(available_slots, many=True)
        return Response(serializer.data)


class DeleteTimeSlotView(APIView):
    """
    Deleta um único horário pelo ID.
    """
    permission_classes = [permissions.IsAuthenticated, IsBarber]
    def delete(self, request, time_slot_id):
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id)
            time_slot.delete()
            return Response({"message": "Horário excluído com sucesso"}, status=status.HTTP_204_NO_CONTENT)
        except TimeSlot.DoesNotExist:
            return Response({"error": "Horário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
