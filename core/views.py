# core/views.py
from django.shortcuts import render

def dashboard_view(request):
    """
    View principal para o Dashboard e Relatório Rápido do Mês Atual.
    """
    context = {
        # Estes dados serão preenchidos com consultas ao banco de dados no futuro
        'entradas': 0, 
        'saidas': 0,
        'saldo': 0
    }
    # Certifique-se de que o arquivo templates/dashboard.html existe!
    return render(request, 'dashboard.html', context)