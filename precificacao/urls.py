# precificacao/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.precificacao_view, name='precificacao'),
]
