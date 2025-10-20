# project_settings/urls.py
from django.contrib import admin
from django.urls import path, include
from core.views import dashboard_view

urlpatterns = [
    # Rotas de Autenticação (Login e Logout)
    path('accounts/', include('django.contrib.auth.urls')), # NOVO: Inclui URLs como 'login', 'logout', 'password_change', etc.
    
    path('', dashboard_view, name='dashboard'), 
    path('admin/', admin.site.urls),
    
    path('vendas/', include('vendas.urls')),       
    path('clientes/', include('clientes.urls')),   
    path('financeiro/', include('financeiro.urls')), # Certifique-se de que o arquivo urls.py foi criado no app financeiro
]