from django.urls import path
from .views import AvailableTimeSlotsView, DeleteSlotsView, DeleteTimeSlotView, GenerateSlotsView, WorkDayListCreateView, WorkDayDetailAPIView, WorkDayPublicListView

urlpatterns = [
    path('', WorkDayListCreateView.as_view(), name='workday-list-create'),
    path('public/', WorkDayPublicListView.as_view(), name='workday-public-list'),
    path('<int:pk>/', WorkDayDetailAPIView.as_view(), name='workday-detail'),
    path('generate-slots/<int:work_day_id>/', GenerateSlotsView.as_view(), name='generate-slots'),
    path('delete-slots/<int:work_day_id>/', DeleteSlotsView.as_view(), name='delete-slots'),
    path('available-time-slot/<int:work_day_id>/', AvailableTimeSlotsView.as_view(), name='available_time_slots'),
    path('delete-time-slot/<int:time_slot_id>/', DeleteTimeSlotView.as_view(), name='delete_time_slot'),
]