from django.urls import path
from .views import ConfirmAppintmentAPIView, CreateAppointmentAPIView, CancelAppointmentAPIView, BarberStatisticsAPIView, ClientStatisticsAPIView, BarberAppointmentsListView, CompleteAppointmentAPIView

urlpatterns = [
    path('create/', CreateAppointmentAPIView.as_view(), name='create-appointment'),
    path('cancel/<int:appointment_id>/', CancelAppointmentAPIView.as_view(), name='cancel-appointment'),
    path('confirm/<int:appointment_id>/', ConfirmAppintmentAPIView.as_view(), name='confirm-appointment'),
    path('complete/<int:appointment_id>/', CompleteAppointmentAPIView.as_view(), name='complete-appointment'),
    path('barber/statistics/', BarberStatisticsAPIView.as_view(), name='barber-statistics'),
    path('client/statistics/', ClientStatisticsAPIView.as_view(), name='client-statistics'),
    path('barber/appointments/', BarberAppointmentsListView.as_view(), name='barber-appointments-list'),
]