# vendas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('lancar/', views.lancamento_vendas_view, name='vendas_lancar'),
    path('buscar-cliente/', views.buscar_cliente_ajax, name='vendas_buscar_cliente_ajax'),
]