# financeiro/urls.py (CORRIGIDO)

from django.urls import path
from . import views

urlpatterns = [
    # Tela para lançamento de Saídas/Gastos (Requisito do Formulário)
    path('saidas/', views.lancamento_saidas_view, name='saidas_lancar'),
    
    # Relatório onde escolhe o mês e compara as vendas (Link do Menu)
    path('mensais/', views.relatorios_mensais_view, name='relatorios_mensais'),
    
    # ⭐️ ROTAS ADICIONADAS PARA CORRIGIR O NoReverseMatch:
    # Rota de Edição
    path('editar/<int:pk>/', views.editar_movimentacao, name='editar_movimentacao'),
    
    # Rota de Exclusão
    path('excluir/<int:pk>/', views.excluir_movimentacao, name='excluir_movimentacao'),
    
    # Você pode remover a rota comentada abaixo, pois já adicionamos as novas.
    # path('movimentacao/<int:pk>/editar/', views.movimentacao_editar_view, name='movimentacao_editar'),
]