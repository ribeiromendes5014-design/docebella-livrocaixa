# vendas/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone 
from datetime import date, datetime
from decimal import Decimal
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# Importa Modelos
from clientes.models import Cliente, CashbackMovimento, Divida
from financeiro.models import FormaPagamento, Movimentacao, Categoria
from .models import Venda, Produto 

# Taxa de Cashback (3%)
TAXA_CASHBACK = Decimal('0.03') 

# ===================================================================
# FUNÇÕES HELPERS DE SALVAMENTO (Processam o POST)
# ===================================================================

def salvar_venda(request):
    """ Processa o POST do formulário de Entrada (Venda). """
    try:
        # 1. Coleta de Dados
        cliente_id = request.POST.get('cliente')
        data_venda_str = request.POST.get('data_venda')
        
        valor_total = Decimal(request.POST.get('valor_total', '0.00') or '0.00')
        valor_cashback_utilizado = Decimal(request.POST.get('valor_cashback_utilizado', '0.00') or '0.00')
        forma_pagamento_id = request.POST.get('forma_pagamento')
        status_pagamento = request.POST.get('status_pagamento')
        data_vencimento = request.POST.get('data_vencimento')

        # Converte data_venda
        data_venda = datetime.strptime(data_venda_str, '%Y-%m-%dT%H:%M').astimezone(timezone.get_current_timezone()) if data_venda_str else timezone.now()
        
        # 2. Objetos Chave
        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        forma_pagamento = FormaPagamento.objects.get(pk=forma_pagamento_id)
        
        # --- CÁLCULOS ESSENCIAIS ---
        valor_recebido_liquido = valor_total - valor_cashback_utilizado
        valor_cashback_gerado = valor_total * TAXA_CASHBACK
        
        with transaction.atomic():
            
            # 3. CRIAÇÃO DA MOVIMENTAÇÃO FINANCEIRA (ENTRADA)
            try:
                categoria_venda = Categoria.objects.get(nome='VENDAS', tipo='E') 
            except ObjectDoesNotExist:
                categoria_venda = Categoria.objects.create(nome='VENDAS', tipo='E') 

            movimentacao_caixa = Movimentacao.objects.create(
                tipo='E',
                valor=valor_recebido_liquido, 
                descricao=f"Venda para {cliente.nome if cliente else 'Avulso'}",
                categoria=categoria_venda,
                forma_pagamento=forma_pagamento,
                status=status_pagamento,
                data_lancamento=data_venda.date(),
                data_vencimento=data_vencimento if data_vencimento else None
            )

            # 4. CRIAÇÃO DO REGISTRO DE VENDA
            venda = Venda.objects.create(
                cliente=cliente,
                valor_total=valor_total,
                valor_cashback_utilizado=valor_cashback_utilizado,
                valor_cashback_gerado=valor_cashback_gerado,
                forma_pagamento=forma_pagamento,
                data_venda=data_venda, 
                movimentacao_caixa=movimentacao_caixa,
            )
            
            # 5. ATUALIZAÇÃO DO SISTEMA DE FIDELIDADE/DÍVIDAS
            
            if cliente and valor_cashback_gerado > 0:
                CashbackMovimento.objects.create(cliente=cliente, tipo='G', valor=valor_cashback_gerado, venda_referencia=venda)
            if cliente and valor_cashback_utilizado > 0:
                CashbackMovimento.objects.create(cliente=cliente, tipo='R', valor=-valor_cashback_utilizado, venda_referencia=venda)
            if status_pagamento in ['PENDENTE', 'DIVIDA'] and cliente and valor_recebido_liquido > 0:
                Divida.objects.create(cliente=cliente, valor_original=valor_recebido_liquido, valor_pendente=valor_recebido_liquido, data_vencimento=data_vencimento)

        return redirect('dashboard')
            
    except ObjectDoesNotExist as e:
        print(f"ERRO DE CHAVE (Venda): {e}")
        return redirect('novo_lancamento') 
    except Exception as e:
        print(f"ERRO GERAL AO SALVAR VENDA: {e}")
        return redirect('novo_lancamento') 

def salvar_saida(request):
    """ Processa o POST do formulário de Saída (Gasto). """
    try:
        # 1. Coleta de Dados (Usando nomes de campos que o form Saída deve ter)
        valor = Decimal(request.POST.get('valor_saida', '0.00') or '0.00')
        descricao = request.POST.get('descricao_saida')
        categoria_id = request.POST.get('categoria_saida')
        forma_pagamento_id = request.POST.get('forma_pagamento_saida')
        status = request.POST.get('status_saida')
        data_vencimento = request.POST.get('data_vencimento_saida')
        data_lancamento_str = request.POST.get('data_lancamento_saida')

        if valor <= 0 or not categoria_id or not forma_pagamento_id:
             raise ValueError("Valor, Categoria e Forma de Pagamento são obrigatórios para Saída.")

        categoria = Categoria.objects.get(pk=categoria_id)
        forma_pagamento = FormaPagamento.objects.get(pk=forma_pagamento_id)
        
        data_lancamento = datetime.strptime(data_lancamento_str, '%Y-%m-%d').date() if data_lancamento_str else timezone.now().date()
        
        with transaction.atomic():
            Movimentacao.objects.create(
                tipo='S', 
                valor=valor,
                descricao=descricao,
                categoria=categoria,
                forma_pagamento=forma_pagamento,
                status=status,
                data_lancamento=data_lancamento,
                data_vencimento=data_vencimento if data_vencimento else None
            )

        return redirect('dashboard')
            
    except Exception as e:
        print(f"ERRO AO SALVAR SAÍDA: {e}")
        return redirect('novo_lancamento') 


# ===================================================================
# 2. VIEW PRINCIPAL (UNIFICADA)
# ===================================================================
@require_http_methods(["GET", "POST"])
def novo_lancamento_view(request):
    
    if request.method == 'POST':
        tipo_lancamento = request.POST.get('tipo_lancamento') 

        if tipo_lancamento == 'ENTRADA':
            return salvar_venda(request)
        
        elif tipo_lancamento == 'SAIDA':
            return salvar_saida(request)
            
        else:
            return redirect('novo_lancamento') # Tipo inválido

    # Lógica GET para RENDERIZAR
    elif request.method == 'GET':
        data_atual = timezone.now().strftime('%Y-%m-%d')
        data_hora_atual = timezone.now().strftime('%Y-%m-%dT%H:%M')
        
        context = {
            'formas_pagamento': FormaPagamento.objects.all(),
            'categorias_saida': Categoria.objects.filter(tipo='S').order_by('nome'),
            'data_venda_default': data_hora_atual,
            'data_atual': data_atual
        }
        return render(request, 'vendas/novo_lancamento.html', context)

# ... (View buscar_cliente_ajax permanece abaixo, ou mova ela para o novo arquivo) ...

def buscar_cliente_ajax(request):
    """ Busca o cliente pelo ID OU nome e retorna o saldo de cashback e dívidas. """
    query = request.GET.get('query')
    
    cliente = None
    
    if query:
        if query.isdigit():
            try:
                cliente = Cliente.objects.get(pk=query)
            except Cliente.DoesNotExist:
                pass 

        if not cliente:
            cliente_exato = Cliente.objects.filter(Q(nome__iexact=query) | Q(apelido__iexact=query)).first()
            if cliente_exato:
                cliente = cliente_exato
            else:
                cliente = Cliente.objects.filter(Q(nome__icontains=query) | Q(apelido__icontains=query)).first()

    if cliente:
        data = {
            'encontrado': True,
            'id': cliente.id,
            'nome': str(cliente), 
            'saldo_cashback': float(cliente.saldo_cashback), 
            'divida_total': float(cliente.divida_total),      
        }
    else:
        data = {
            'encontrado': False,
            'mensagem': 'Cliente não encontrado. Deseja cadastrar agora?',
            'nome_sugerido': query 
        }
        
    return JsonResponse(data)
