from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsBarber, IsClient
from core.utils.utils import get_current_english_weekday
from schedule.models import WorkDay
from services.models import Services
from .models import Appointment
from django.db.models import Sum, Count, Q
from .serializers import AppointmentSerializer
from django.utils.timezone import now, timedelta
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema


class CreateAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Cria um novo agendamento para o cliente autenticado, vinculando o horário (time_slot) e marcando-o como indisponível.",
        request_body=AppointmentSerializer,
        responses={
            201: AppointmentSerializer,
            400: "Erro de validação ou horário já ocupado.",
        }
    )
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

    @swagger_auto_schema(
        operation_description="Cancela um agendamento, liberando o time_slot correspondente. O cancelamento pode ser feito pelo cliente ou pelo barbeiro responsável.",
        responses={
            200: "Agendamento cancelado com sucesso.",
            404: "Agendamento não encontrado.",
            403: "Usuário não autorizado a cancelar o agendamento.",
        }
    )
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

    @swagger_auto_schema(
        operation_description="Confirma um agendamento. A confirmação pode ser realizada apenas pelo barbeiro responsável.",
        responses={
            200: "Agendamento confirmado com sucesso.",
            404: "Agendamento não encontrado.",
            403: "Usuário não autorizado a confirmar o agendamento.",
        }
    )
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

    @swagger_auto_schema(
        operation_description="Retorna as estatísticas de agendamentos para o barbeiro autenticado nos últimos 30 dias, incluindo o total de agendamentos, quantidade confirmada e cancelada.",
        responses={
            200: "Estatísticas de agendamentos do barbeiro.",
            403: "Usuário não autorizado. Necessário ser barbeiro autenticado.",
        }
    )
    def get(self, request):
        """
        Retorna estatísticas de agendamentos para o barbeiro autenticado.
        """
        barber = request.user
        last_30_days = now() - timedelta(days=30)

        # Agendamentos nos últimos 30 dias
        appointments_last_30_days = Appointment.objects.filter(barber=barber, created_at__gte=last_30_days)

        confirmed_last_30 = appointments_last_30_days.filter(status=Appointment.Status.CONFIRMED)
        canceled_last_30 = appointments_last_30_days.filter(status=Appointment.Status.CANCELED)
        revenue_last_30 = confirmed_last_30.aggregate(total=Sum('price'))['total'] or 0

        # Total de agendamentos por status
        total_appointments = Appointment.objects.filter(barber=barber)
        status_counts = {
            status: total_appointments.filter(status=status).count()
            for status, _ in Appointment.Status.choices
        }

        # Agendamentos do dia atual
        current_day = get_current_english_weekday()
        work_day_today = WorkDay.objects.filter(barber=barber,day_of_week=current_day).first()
        upcoming_appointments = []
        if work_day_today:
            current_time = datetime.now().time()
            time_slots = work_day_today.time_slots.filter(time__gte=current_time)
            upcoming_appointments = Appointment.objects.filter(time_slot__in=time_slots,status__in=[Appointment.Status.CONFIRMED]).select_related('client', 'service', 'time_slot').order_by('time_slot__time')

        # Serviços mais populares (últimos 30 dias)
        popular_services = Services.objects.filter(
            barber=barber,
            is_active=True
        ).annotate(
            total_appointments=Count(
                'appointment',
                filter=Q(
                    appointment__status=Appointment.Status.CONFIRMED,
                    appointment__created_at__gte=last_30_days
                )
            )
        ).order_by('-total_appointments')[:3]
        
        # Faturamento total histórico
        gross_revenue = Appointment.objects.filter(
            barber=barber,
            status=Appointment.Status.CONFIRMED
        ).aggregate(total=Sum('price'))['total'] or 0

        return Response({
            "barber": barber.username,
            "last_30_days_stats": {
                "total_appointments": appointments_last_30_days.count(),
                "confirmed": confirmed_last_30.count(),
                "canceled": canceled_last_30.count(),
                "revenue": float(revenue_last_30),
                "status_distribution": status_counts,
            },
            "today_upcoming_appointments": [
                {
                    "id": appointment.id,
                    "client": appointment.client.username,
                    "service": appointment.service.name,
                    "time": appointment.time_slot.time.strftime("%H:%M"),
                    "status": appointment.status
                } for appointment in upcoming_appointments
            ],
            "most_popular_services": [
                {
                    "service": service.name,
                    "appointments_count": service.total_appointments,
                    "price": float(service.price)
                } for service in popular_services if service.total_appointments > 0
            ],
            "financial_metrics": {
                "lifetime_gross_revenue": float(gross_revenue),
                "last_30_days_revenue": float(revenue_last_30)
            }
        })


class ClientStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsClient]

    @swagger_auto_schema(
        operation_description="Retorna as estatísticas e a lista de agendamentos do cliente autenticado.",
        responses={
            200: "Estatísticas de agendamentos do cliente, incluindo lista detalhada dos agendamentos.",
            403: "Usuário não autorizado. Necessário ser cliente autenticado.",
        }
    )
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
