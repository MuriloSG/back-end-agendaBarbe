from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/services/', include('services.urls')),
    path('api/v1/schedule/', include('schedule.urls')),
    path('api/v1/appointments/', include('appointments.urls')),
]
