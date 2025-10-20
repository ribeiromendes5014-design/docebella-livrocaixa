# clientes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Lista de Clientes (com Saldo Cashback e Dívidas) - Link do Menu
    # Rota: /clientes/
    path('', views.clientes_lista_view, name='clientes_lista'),
    
    # 2. Detalhe do Cliente (Histórico de Compras/Dívidas)
    # Rota: /clientes/123/
    path('<int:pk>/', views.cliente_detalhe_view, name='cliente_detalhe'),
    
    # 3. Cadastro Rápido (Endpoint AJAX)
    # Rota: /clientes/cadastrar-rapido/
    path('cadastrar-rapido/', views.cadastro_rapido_ajax, name='clientes_cadastro_rapido_ajax'),
]