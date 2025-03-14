from django.urls import path
from .views import ServicoListCreateView, ServicoDetailView, ServicoPublicListView

urlpatterns = [
    # URL para listar e criar serviços
    path('', ServicoListCreateView.as_view(),name='servico-list-create'),

    # URL para detalhes, atualização (PUT/PATCH) e exclusão (DELETE) de um serviço específico
    path('<int:pk>/', ServicoDetailView.as_view(),name='servico-detail'),

    # URL para lista pública de serviços ativos
    path('public/', ServicoPublicListView.as_view(),name='servico-public-list'),
]
