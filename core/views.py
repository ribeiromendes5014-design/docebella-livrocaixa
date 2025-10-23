from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    """
    View principal para o Dashboard e Relatório Rápido do Mês Atual.
    """
    context = {
        'entradas': 0, 
        'saidas': 0,
        'saldo': 0
    }
    return render(request, 'dashboard.html', context)


@login_required
def relatorios_view(request):
    """
    Página de Relatórios (gráficos e estatísticas)
    """
    return render(request, 'relatorios.html')
