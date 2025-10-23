# project_settings/urls.py
from django.contrib import admin
from django.urls import path, include
from core import views as core_views  # ✅ Importa todas as views do core (inclusive relatorios_view)

urlpatterns = [
    # Rotas de Autenticação (Login e Logout)
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout prontos

    # Páginas principais
    path('', core_views.dashboard_view, name='dashboard'),
    path('relatorios/', core_views.relatorios_view, name='relatorios'),  # ✅ ADICIONADA

    # Admin do Django
    path('admin/', admin.site.urls),

    # Apps
    path('vendas/', include('vendas.urls')),
    path('clientes/', include('clientes.urls')),
    path('financeiro/', include('financeiro.urls')),
]
