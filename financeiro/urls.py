# financeiro/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Tela para lançamento de Saídas/Gastos (Requisito do Formulário)
    path('saidas/', views.lancamento_saidas_view, name='saidas_lancar'),
    
    # Relatório onde escolhe o mês e compara as vendas (Link do Menu)
    path('mensais/', views.relatorios_mensais_view, name='relatorios_mensais'),
    
    # Rotas de edição/exclusão (Opcional, mas útil)
    # path('movimentacao/<int:pk>/editar/', views.movimentacao_editar_view, name='movimentacao_editar'),
]