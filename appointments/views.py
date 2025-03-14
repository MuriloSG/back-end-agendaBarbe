from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsBarber, IsClient
from .models import Appointment
from .serializers import AppointmentSerializer
from django.utils.timezone import now, timedelta


class CreateAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request):
        """
        Cria um novo agendamento, vinculando o cliente autenticado e marcando
        o time_slot como indisponível.
        """
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            time_slot = serializer.validated_data["time_slot"]

            if not time_slot.is_available:
                return Response(
                    {"error": "Este horário já está ocupado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Cria o agendamento e marca o horário como ocupado
            appointment = serializer.save(client=request.user)
            time_slot.is_available = False
            time_slot.save()

            return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        """
        Cancela um agendamento, liberando o time_slot correspondente.
        O cancelamento pode ser feito pelo cliente ou pelo barbeiro responsável.
        """
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Agendamento não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.user != appointment.client and request.user != appointment.barber:
            return Response(
                {"error": "Você não tem permissão para cancelar este agendamento."},
                status=status.HTTP_403_FORBIDDEN,
            )

        appointment.status = Appointment.Status.CANCELED
        appointment.time_slot.is_available = True
        appointment.time_slot.save()
        appointment.save()

        return Response(
            {"message": "Agendamento cancelado com sucesso."},
            status=status.HTTP_200_OK,
        )

class ConfirmAppintmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBarber]

    def post(self, request, appointment_id):
        """
        Confirma um agendamento
        """
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Agendamento não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        appointment.status = Appointment.Status.CONFIRMED
        appointment.time_slot.save()
        appointment.save()

        return Response(
            {"message": "Agendamento confirmado com sucesso."},
            status=status.HTTP_200_OK,
        )

class BarberStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBarber]

    def get(self, request):
        """
        Retorna estatísticas de agendamentos para o barbeiro autenticado.
        """
        barber = request.user
        last_30_days = now() - timedelta(days=30)

        # Agendamentos nos últimos 30 dias
        appointments_last_30_days = Appointment.objects.filter(barber=barber, created_at__gte=last_30_days)

        confirmed_count = appointments_last_30_days.filter(status=Appointment.Status.CONFIRMED).count()
        canceled_count = appointments_last_30_days.filter(status=Appointment.Status.CANCELED).count()

        # Total de agendamentos por status
        total_appointments = Appointment.objects.filter(barber=barber)
        status_counts = {
            status: total_appointments.filter(status=status).count()
            for status, _ in Appointment.Status.choices
        }

        return Response({
            "barber": barber.username,
            "total_appointments_last_30_days": appointments_last_30_days.count(),
            "confirmed_last_30_days": confirmed_count,
            "canceled_last_30_days": canceled_count,
            "total_appointments": total_appointments.count(),
            "appointments_by_status": status_counts,
        })


class ClientStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    def get(self, request):
        """
        Retorna estatísticas e lista de agendamentos para o cliente autenticado.
        """
        client = request.user
        appointments = Appointment.objects.filter(client=client)
        total_appointments = appointments.count()
        appointment_list = [
            {
                "id": appointment.id,
                "service": appointment.service.name,
                "status": appointment.status,
                "time_slot": str(appointment.time_slot.time),
                "price": appointment.price,
                "is_free": appointment.is_free,
                "created_at": appointment.created_at
            }
            for appointment in appointments
        ]

        return Response({
            "client": client.username,
            "total_appointments": total_appointments,
            "appointments": appointment_list
        })
