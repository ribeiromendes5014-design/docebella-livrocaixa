# project_settings/urls.py
from django.contrib import admin
from django.urls import path, include
from core.views import dashboard_view

urlpatterns = [
    # Rotas de Autenticação (Login e Logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # Página inicial (Dashboard)
    path('', dashboard_view, name='dashboard'),

    # Painel admin
    path('admin/', admin.site.urls),

    # Apps principais
    path('vendas/', include('vendas.urls')),
    path('clientes/', include('clientes.urls')),
    path('financeiro/', include('financeiro.urls')),

    # 🆕 Novo app de precificação
    path('precificacao/', include('precificacao.urls')),
]
