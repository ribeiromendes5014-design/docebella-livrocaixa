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
]
