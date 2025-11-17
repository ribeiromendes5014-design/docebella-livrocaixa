# financeiro/views.py
from django.shortcuts import render, get_object_or_404, redirect
from vendas.models import Venda
# ATENÇÃO: Se Movimentacao usa FormaPagamento, você precisa importá-lo
from financeiro.models import Movimentacao, Categoria, FormaPagamento 
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
from datetime import datetime
import calendar
from django.db.models import F
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import MovimentacaoForm # Deve funcionar agora que criamos o forms.py


# ===================================================================
# 1. VIEW DE LANÇAMENTO DE SAÍDAS (GASTOS)
# ===================================================================
def lancamento_saidas_view(request):
    """
    Renderiza o formulário para registrar uma saída de caixa.
    """
    context = {}
    return render(request, 'financeiro/lancamento_saidas.html', context)

# ===================================================================
# 2. VIEW DE RELATÓRIOS MENSAIS (RELATORIOS DETALHADOS)
# ===================================================================
def relatorios_mensais_view(request):
    # --- 1. DEFINIÇÃO DO PERÍODO DE FILTRO ---
    
    mes_inicio_str = request.GET.get('mes_inicio')
    mes_fim_str = request.GET.get('mes_fim')
    
    hoje = date.today()
    
    if mes_inicio_str and mes_fim_str:
        try:
            data_inicio = datetime.strptime(mes_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(mes_fim_str, '%Y-%m-%d').date()
            
            ultimo_dia = calendar.monthrange(data_fim.year, data_fim.month)[1]
            data_fim = data_fim.replace(day=ultimo_dia)
            
        except ValueError:
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
    else:
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
    
    # --- 2. CÁLCULO FINANCEIRO PARA O PERÍODO ESCOLHIDO (RESUMO) ---
    
    movs_periodo = Movimentacao.objects.filter(
        data_lancamento__range=[data_inicio, data_fim],
        status='PAGO'
    ).select_related('categoria')
    
    entradas_periodo = movs_periodo.filter(tipo='E').aggregate(total=Sum('valor'))['total'] or Decimal(0)
    saidas_periodo = movs_periodo.filter(tipo='S').aggregate(total=Sum('valor'))['total'] or Decimal(0)
    
    saldo_periodo = entradas_periodo - saidas_periodo

    
    # --- 3. DADOS PARA TABELA DETALHADA (TODOS OS LANÇAMENTOS) ---
    
    # CORREÇÃO DA QUERY: Adicionando cliente_fornecedor e alinhando indentação
    movimentacoes_do_mes = Movimentacao.objects.select_related(
        'categoria', 
        'forma_pagamento',
        'cliente_fornecedor' # BUSCA O OBJETO CLIENTE/FORNECEDOR
    ).filter(
        data_lancamento__range=[data_inicio, data_fim]
    ).order_by('-data_lancamento')
    
    
    # --- 4. DADOS PARA GRÁFICO DE CRESCIMENTO (Últimos 12 meses) ---
    
    data_12_meses_atras = hoje - timedelta(days=365)
    
    vendas_mensais = Venda.objects.filter(
        data_venda__gte=data_12_meses_atras
    ).annotate(
        mes_ano=TruncMonth('data_venda')
    ).values('mes_ano').annotate(
        total_vendas=Sum('valor_total')
    ).order_by('mes_ano')
    
    dados_grafico = [
        {'mes': item['mes_ano'].strftime('%Y-%m'), 
         'valor': float(item['total_vendas'])}
        for item in vendas_mensais
    ]
        
    context = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        
        # Dados de Resumo
        'entradas_periodo': entradas_periodo,
        'saidas_periodo': saidas_periodo,
        'saldo_periodo': saldo_periodo,
        
        # Dados para a Tabela Detalhada
        'movimentacoes_do_mes': movimentacoes_do_mes, 
        
        # Dados do Gráfico
        'dados_grafico_json': dados_grafico,
    }
    return render(request, 'financeiro/relatorios_mensais.html', context)


# ===================================================================
# 3. VIEWS DE EDIÇÃO E EXCLUSÃO (DEPENDEM DE forms.py)
# ===================================================================

@login_required 
def editar_movimentacao(request, pk):
    movimentacao = get_object_or_404(Movimentacao, pk=pk)
    
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, instance=movimentacao)
        if form.is_valid():
            form.save()
            return redirect('relatorios_mensais')
    else:
        form = MovimentacaoForm(instance=movimentacao)
        
    context = {
        'form': form,
        'movimentacao': movimentacao,
        'titulo': 'Editar Movimentação'
    }
    # Este template deve ser criado: financeiro/editar_movimentacao.html
    return render(request, 'financeiro/editar_movimentacao.html', context)


@login_required 
def excluir_movimentacao(request, pk):
    movimentacao = get_object_or_404(Movimentacao, pk=pk)
    
    if request.method == 'POST':
        movimentacao.delete()
        return redirect('relatorios_mensais') 
        
    context = {
        'movimentacao': movimentacao,
        'titulo': 'Confirmar Exclusão'
    }
    # Este template deve ser criado: financeiro/excluir_movimentacao_confirm.html
    return render(request, 'financeiro/excluir_movimentacao_confirm.html', context)