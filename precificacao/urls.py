# precificacao/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.precificacao_view, name='precificacao'),
    path('editar/<int:pk>/', views.editar_produto, name='editar_produto'),
    path('excluir/<int:pk>/', views.excluir_produto, name='excluir_produto'),
]
