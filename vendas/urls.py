# vendas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # NOVO: Tela Unificada de Lançamento (Entrada ou Saída)
    path('novo-lancamento/', views.novo_lancamento_view, name='novo_lancamento'),
    
    # Endpoint para consulta rápida de cliente (Ainda necessária para AJAX)
    path('buscar-cliente/', views.buscar_cliente_ajax, name='vendas_buscar_cliente_ajax'),
]
