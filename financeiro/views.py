# financeiro/views.py (Corrigido)
from django.shortcuts import render
from vendas.models import Venda
from financeiro.models import Movimentacao, Categoria
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date, timedelta
import calendar
from django.db.models import F
from decimal import Decimal # ⭐️ IMPORTAR DECIMAL

# ===================================================================
# 1. VIEW DE LANÇAMENTO DE SAÍDAS (GASTOS)
# ... (código inalterado)

# ===================================================================
# 2. VIEW DE RELATÓRIOS MENSAIS (RELATORIOS DETALHADOS)
# URL Name: 'relatorios_mensais'
# ===================================================================
def relatorios_mensais_view(request):
    # --- 1. DEFINIÇÃO DO PERÍODO DE FILTRO ---
    
    # Parâmetros de filtro (pode ser mês/ano específicos ou um período)
    mes_inicio_str = request.GET.get('mes_inicio')
    mes_fim_str = request.GET.get('mes_fim')
    
    hoje = date.today()
    
    # Se não houver filtro, o padrão é o MÊS ATUAL
    if mes_inicio_str and mes_fim_str:
        # Modo Personalizado: Filtro de Período
        try:
            # Note: data_inicio precisa ser date/datetime para range funcionar corretamente
            data_inicio = datetime.strptime(mes_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(mes_fim_str, '%Y-%m-%d').date()
            
            # Ajusta para o final do mês, se necessário (depende da granularidade)
            # Como você usa date__range, a correção aqui não é estritamente necessária,
            # mas manteremos a lógica se você quiser garantir o final do mês
            ultimo_dia = calendar.monthrange(data_fim.year, data_fim.month)[1]
            data_fim = data_fim.replace(day=ultimo_dia)
            
        except ValueError:
            # Em caso de formato inválido, volta para o padrão
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
    else:
        # Modo Padrão: Mês Atual (Requisito)
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
    
    # --- 2. CÁLCULO FINANCEIRO PARA O PERÍODO ESCOLHIDO ---
    
    # Filtra todas as movimentações PAGO/RECEBIDO dentro do período
    movs_periodo = Movimentacao.objects.filter(
        data_lancamento__range=[data_inicio, data_fim],
        status='PAGO'
    ).select_related('categoria')
    
    # ⭐️ CORREÇÃO: Usar Decimal(0) como fallback para manter a consistência de tipos
    entradas_periodo = movs_periodo.filter(tipo='E').aggregate(total=Sum('valor'))['total'] or Decimal(0)
    saidas_periodo = movs_periodo.filter(tipo='S').aggregate(total=Sum('valor'))['total'] or Decimal(0)
    
    # Linha 71: Agora a subtração é Decimal - Decimal (CORRETO)
    saldo_periodo = entradas_periodo - saidas_periodo
    
    # --- 3. DADOS PARA GRÁFICO DE CRESCIMENTO (Últimos 12 meses) ---
    
    # Calcula a data de 1 ano atrás
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
         'valor': float(item['total_vendas'])} # Mantido float() para serialização do gráfico
        for item in vendas_mensais
    ]
        
    context = {
        'data_inicio': data_inicio.strftime('%Y-%m-%d'),
        'data_fim': data_fim.strftime('%Y-%m-%d'),
        'entradas_periodo': entradas_periodo,
        'saidas_periodo': saidas_periodo,
        'saldo_periodo': saldo_periodo,
        
        'dados_grafico_json': dados_grafico,
    }
    return render(request, 'financeiro/relatorios_mensais.html', context)
