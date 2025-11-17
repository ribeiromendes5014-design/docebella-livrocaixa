from django.urls import path
from . import views

urlpatterns = [
    # 1. Lista de Clientes (com Saldo Cashback e Dívidas)
    path('', views.clientes_lista_view, name='clientes_lista'),

    # 2. Detalhe do Cliente (Histórico de Compras/Dívidas)
    path('<int:pk>/', views.cliente_detalhe_view, name='cliente_detalhe'),

    # 3. Cadastro Rápido (AJAX)
    path('cadastrar-rapido/', views.cadastro_rapido_ajax, name='clientes_cadastro_rapido_ajax'),

    # 4. Exclusão de Cliente (via botão)
    path('excluir/<int:cliente_id>/', views.excluir_cliente, name='clientes_excluir'),

    # 5. Quitar Dívida (do Modal)
    path('quitar-divida/<int:pk>/', views.clientes_quitar_divida_view, name='clientes_quitar_divida'),

    # 6. Excluir Movimentação de Cashback
    path('cashback/excluir/<int:movimento_id>/', views.excluir_movimento_cashback_view, name='clientes_excluir_cashback'),

    # 7. Excluir Venda do Histórico
    path('venda/excluir/<int:venda_id>/', views.excluir_venda_view, name='clientes_excluir_venda'),
]
