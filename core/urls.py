from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="API para web site para Barbearias",
        default_version='v1',
        description="API para gerenciar os agendamentos e serviços de um website para barbearias.",
        contact=openapi.Contact(email="msg@aluno.ifnmg.edu.br"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/services/', include('services.urls')),
    path('api/v1/schedule/', include('schedule.urls')),
    path('api/v1/appointments/', include('appointments.urls')),
    # Documentação
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
