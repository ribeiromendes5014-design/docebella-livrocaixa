# vendas/urls.py (Versão FINAL e CORRIGIDA)
from django.urls import path
from . import views

urlpatterns = [
    # O nome da URL continua 'vendas_lancar' e aponta para a View Unificada
    path('lancar/', views.lancamento_vendas_view, name='vendas_lancar'), 
    
    # URL de busca AJAX (permanece)
    path('buscar-cliente/', views.buscar_cliente_ajax, name='vendas_buscar_cliente_ajax'),
]
