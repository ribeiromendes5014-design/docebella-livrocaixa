# vendas/urls.py (NÃO PRECISA DE ALTERAÇÃO - APENAS GARANTIR QUE APONTE PARA A NOVA VIEW)
from django.urls import path
from . import views

urlpatterns = [
    # O nome da URL continua 'vendas_lancar'
    path('lancar/', views.novo_lancamento_view, name='vendas_lancar'), 
    
    # Endpoint para consulta AJAX (permanece)
    path('buscar-cliente/', views.buscar_cliente_ajax, name='vendas_buscar_cliente_ajax'),
]
