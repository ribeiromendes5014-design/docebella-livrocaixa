from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
]
