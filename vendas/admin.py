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
# 1. VIEW DE LANÇAMENTO DE VENDAS (GET para Formulário, POST para Salvar)
# ===================================================================
@require_http_methods(["GET", "POST"])
def lancamento_vendas_view(request):
    
    # Lógica para salvar a venda (POST)
    if request.method == 'POST':
        try:
            # 1. Coleta e Conversão de Dados
            cliente_id = request.POST.get('cliente')
            data_venda_str = request.POST.get('data_venda')
            
            valor_total = Decimal(request.POST.get('valor_total', '0.00'))
            valor_cashback_utilizado = Decimal(request.POST.get('valor_cashback_utilizado', '0.00'))
            forma_pagamento_id = request.POST.get('forma_pagamento')
            status_pagamento = request.POST.get('status_pagamento')
            data_vencimento = request.POST.get('data_vencimento')

            # Converte data_venda
            if data_venda_str:
                data_venda = datetime.strptime(data_venda_str, '%Y-%m-%dT%H:%M').astimezone(timezone.get_current_timezone())
            else:
                data_venda = timezone.now()
            
            # 2. Objetos Chave (Lança exceção se não encontrar a forma de pagamento)
            cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
            forma_pagamento = FormaPagamento.objects.get(pk=forma_pagamento_id)
            
            # --- CÁLCULOS ESSENCIAIS ---
            valor_recebido_liquido = valor_total - valor_cashback_utilizado
            valor_cashback_gerado = valor_total * TAXA_CASHBACK
            
            with transaction.atomic():
                
                # 3. CRIAÇÃO DA MOVIMENTAÇÃO FINANCEIRA (ENTRADA)
                try:
                    categoria_venda = Categoria.objects.get(nome='Vendas', tipo='E') 
                except ObjectDoesNotExist:
                    categoria_venda = Categoria.objects.create(nome='Vendas', tipo='E') 

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
                
                # 5a. Registro do Cashback Gerado (3%)
                if cliente and valor_cashback_gerado > 0:
                    CashbackMovimento.objects.create(
                        cliente=cliente,
                        tipo='G', 
                        valor=valor_cashback_gerado,
                        venda_referencia=venda
                    )

                # 5b. Registro do Cashback Utilizado (Resgate)
                if cliente and valor_cashback_utilizado > 0:
                    CashbackMovimento.objects.create(
                        cliente=cliente,
                        tipo='R', 
                        valor=-valor_cashback_utilizado, 
                        venda_referencia=venda
                    )
                    
                # 5c. Criação da Dívida (se for PENDENTE ou DÍVIDA)
                if status_pagamento in ['PENDENTE', 'DIVIDA'] and cliente and valor_recebido_liquido > 0:
                    Divida.objects.create(
                        cliente=cliente,
                        valor_original=valor_recebido_liquido,
                        valor_pendente=valor_recebido_liquido,
                        data_vencimento=data_vencimento if data_vencimento else None
                    )

            # Redirecionamento após sucesso
            return redirect('dashboard')
            
        except ObjectDoesNotExist:
             # Trata erros específicos de objetos não encontrados (ex: Forma de Pagamento)
             print("ERRO: Objeto Cliente ou Forma de Pagamento não encontrado.")
             return redirect('vendas_lancar') 
        except Exception as e:
            print(f"ERRO AO SALVAR VENDA: {e}")
            return redirect('vendas_lancar') 

    # Carrega dados essenciais para o formulário GET
    elif request.method == 'GET':
        data_atual = timezone.now().strftime('%Y-%m-%dT%H:%M')
        
        context = {
            # ESTA LINHA PEGA OS DADOS DO ADMIN
            'formas_pagamento': FormaPagamento.objects.all(), 
            'produtos': Produto.objects.all(),
            'data_venda_default': data_atual 
        }
        return render(request, 'vendas/lancamento_vendas.html', context)


# ===================================================================
# 2. VIEW DE CONSULTA RÁPIDA (AJAX) 
# ===================================================================
def buscar_cliente_ajax(request):
    """ Busca o cliente pelo ID OU nome e retorna o saldo de cashback e dívidas. """
    query = request.GET.get('query')
    
    cliente = None
    
    if query:
        # Tenta buscar por ID exato se a query for numérica 
        if query.isdigit():
            try:
                cliente = Cliente.objects.get(pk=query)
            except Cliente.DoesNotExist:
                pass 

        # Se não encontrou por ID ou se a query não era numérica, busca por nome (ou parte do nome)
        if not cliente:
            # Prioriza a busca por nome__iexact (exato) e depois por icontains (parcial)
            # Inclui busca por apelido também
            cliente_exato = Cliente.objects.filter(Q(nome__iexact=query) | Q(apelido__iexact=query)).first()
            if cliente_exato:
                cliente = cliente_exato
            else:
                cliente = Cliente.objects.filter(Q(nome__icontains=query) | Q(apelido__icontains=query)).first()

    if cliente:
        # Retorna os dados
        data = {
            'encontrado': True,
            'id': cliente.id,
            'nome': str(cliente), 
            'saldo_cashback': float(cliente.saldo_cashback), 
            'divida_total': float(cliente.divida_total),      
        }
    else:
        # Sugere cadastro
        data = {
            'encontrado': False,
            'mensagem': 'Cliente não encontrado. Deseja cadastrar agora?',
            'nome_sugerido': query 
        }
        
    return JsonResponse(data)