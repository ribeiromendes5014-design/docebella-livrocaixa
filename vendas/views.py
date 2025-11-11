# vendas/views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta

# Importa Modelos
from clientes.models import Cliente, CashbackMovimento, Divida
from financeiro.models import FormaPagamento, Movimentacao, Categoria
from .models import Venda, VendaItem, Produto

# Taxa de Cashback (3%)
TAXA_CASHBACK = Decimal('0.03')


# ===================================================================
# FUNÇÕES HELPERS DE SALVAMENTO (Processam o POST)
# ===================================================================
# vendas/views.py

@login_required
def salvar_venda(request):
    """Processa o POST do formulário de Entrada (Venda) com produtos e observação."""
    try:
        # Nota: O nome do campo no HTML (lançamento_vendas.html) deve ser 'cliente_fornecedor'.
        cliente_id = request.POST.get('cliente_fornecedor', '').strip() 
        data_venda_str = request.POST.get('data_venda')
        valor_total_str = request.POST.get('valor_total', '0').strip().replace(',', '.')
        valor_cashback_utilizado_str = request.POST.get('valor_cashback_utilizado', '0').strip().replace(',', '.')
        observacao = request.POST.get('observacao', '').strip()

        # ⭐️ NOVO: Captura dos dados de parcelamento
        numero_parcelas = int(request.POST.get('numero_parcelas', 1))
        data_primeira_parcela_str = request.POST.get('data_primeira_parcela')
        incluir_entrada = request.POST.get('incluir_entrada') == 'on'


        try:
            valor_total = Decimal(valor_total_str)
        except Exception:
            valor_total = Decimal('0.00')

        try:
            valor_cashback_utilizado = Decimal(valor_cashback_utilizado_str)
        except Exception:
            valor_cashback_utilizado = Decimal('0.00')

        forma_pagamento_id = request.POST.get('forma_pagamento', '').strip()
        status_pagamento = request.POST.get('status_pagamento')
        data_vencimento = request.POST.get('data_vencimento')

        if valor_total <= 0:
            raise ValueError("O Valor Total da Venda deve ser maior que zero.")
        if not forma_pagamento_id:
            raise ValueError("A Forma de Pagamento é obrigatória e não foi selecionada.")

        data_venda = (
            datetime.strptime(data_venda_str, '%Y-%m-%dT%H:%M').astimezone(timezone.get_current_timezone())
            if data_venda_str else timezone.now()
        )

        # Busca o objeto Cliente se o ID for válido (usa o objeto 'cliente')
        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        forma_pagamento = FormaPagamento.objects.get(pk=forma_pagamento_id)

        valor_recebido_liquido = valor_total - valor_cashback_utilizado
        valor_cashback_gerado = valor_total * TAXA_CASHBACK

        with transaction.atomic():
            # Garante categoria 'VENDAS' no financeiro
            try:
                categoria_venda = Categoria.objects.get(nome='VENDAS', tipo='E')
            except ObjectDoesNotExist:
                categoria_venda = Categoria.objects.create(nome='VENDAS', tipo='E')

            # --- LÓGICA DE MOVIMENTAÇÃO: PARCELADA vs. NORMAL ---
            is_parcelado = numero_parcelas > 1

            if is_parcelado and data_primeira_parcela_str:
                valor_a_parcelar = valor_recebido_liquido
                valor_parcela = (valor_a_parcelar / numero_parcelas).quantize(Decimal('0.01'))
                
                # Ajusta a última parcela para evitar diferenças de arredondamento
                valor_ultima_parcela = valor_a_parcelar - (valor_parcela * (numero_parcelas - 1))

                data_base_vencimento = datetime.strptime(data_primeira_parcela_str, '%Y-%m-%d').date()

                for i in range(numero_parcelas):
                    is_entrada = (i == 0 and incluir_entrada)
                    
                    vencimento_parcela = data_base_vencimento + relativedelta(months=i)
                    
                    Movimentacao.objects.create(
                        tipo='E',
                        valor=valor_ultima_parcela if i == numero_parcelas - 1 else valor_parcela,
                        descricao=f"Parcela {i+1}/{numero_parcelas} - Venda para {cliente.nome if cliente else 'Avulso'}",
                        categoria=categoria_venda,
                        forma_pagamento=forma_pagamento,
                        status='PAGO' if is_entrada else 'PENDENTE',
                        data_lancamento=data_venda.date(),
                        data_vencimento=vencimento_parcela,
                        cliente_fornecedor=cliente,
                    )
                # Para a venda, associamos a primeira movimentação ou nenhuma se for tudo a prazo
                movimentacao_caixa = None # Venda parcelada não tem uma única movimentação

            else: # Venda normal (não parcelada)
                movimentacao_caixa = Movimentacao.objects.create(
                    tipo='E',
                    valor=valor_recebido_liquido,
                    descricao=f"Venda para {cliente.nome if cliente else 'Avulso'}",
                    categoria=categoria_venda,
                    forma_pagamento=forma_pagamento,
                    status=status_pagamento,
                    data_lancamento=data_venda.date(),
                    data_vencimento=data_vencimento if data_vencimento else None,
                    cliente_fornecedor=cliente,
                )

            # Cria a venda principal
            venda = Venda.objects.create(
                cliente=cliente,
                valor_total=valor_total,
                valor_cashback_utilizado=valor_cashback_utilizado,
                valor_cashback_gerado=valor_cashback_gerado,
                forma_pagamento=forma_pagamento,
                data_venda=data_venda,
                movimentacao_caixa=movimentacao_caixa, # Pode ser None em vendas parceladas
                observacao=observacao
            )

            # ... (Restante do código de VendaItem, Cashback e Dívidas, sem alterações) ...
            
            # Salva os itens (produtos e quantidades)
            produtos_ids = request.POST.getlist('produtos[]')
            quantidades = request.POST.getlist('quantidades[]')
            valores_unitarios = request.POST.getlist('valores_unitarios[]')

            for i in range(len(produtos_ids)):
                try:
                    produto = Produto.objects.get(pk=produtos_ids[i])
                    qtd = Decimal(quantidades[i])
                    valor_unit = Decimal(valores_unitarios[i])
                    subtotal = qtd * valor_unit

                    VendaItem.objects.create(
                        venda=venda,
                        produto=produto,
                        quantidade=qtd,
                        valor_unitario=valor_unit,
                        subtotal=subtotal
                    )

                    # Atualiza o estoque
                    produto.estoque = max(produto.estoque - int(qtd), 0)
                    produto.save()

                except Exception as item_err:
                    print(f"Erro ao adicionar item da venda: {item_err}")

            # Cashback e dívidas (igual antes)
            if cliente:
                if valor_cashback_gerado > 0:
                    CashbackMovimento.objects.create(
                        cliente=cliente,
                        tipo='G',
                        valor=valor_cashback_gerado,
                        venda_referencia=venda
                    )
                    cliente.saldo_cashback_db = (cliente.saldo_cashback_db or Decimal('0')) + valor_cashback_gerado

                if valor_cashback_utilizado > 0:
                    CashbackMovimento.objects.create(
                        cliente=cliente,
                        tipo='R',
                        valor=-valor_cashback_utilizado,
                        venda_referencia=venda
                    )
                    cliente.saldo_cashback_db = (cliente.saldo_cashback_db or Decimal('0')) - valor_cashback_utilizado

                if status_pagamento in ['PENDENTE', 'DIVIDA'] and valor_recebido_liquido > 0:
                    Divida.objects.create(
                        cliente=cliente,
                        valor_original=valor_recebido_liquido,
                        valor_pendente=valor_recebido_liquido,
                        data_vencimento=data_vencimento
                    )
                    cliente.divida_total_db = (cliente.divida_total_db or Decimal('0')) + valor_recebido_liquido

                cliente.save()

        return redirect('dashboard')

    except Exception as e:
        print(f"ERRO AO SALVAR VENDA: {e}")
        return redirect('vendas_lancar')


# ===================================================================
# FUNÇÃO PARA SAÍDA (GASTOS)
# ===================================================================
@login_required
def salvar_saida(request):
    """Processa o POST do formulário de Saída (Gasto)."""
    try:
        valor_str = request.POST.get('valor_saida', '0').strip().replace(',', '.')
        try:
            valor = Decimal(valor_str)
        except Exception:
            valor = Decimal('0.00')

        descricao = request.POST.get('descricao_saida')
        categoria_id = request.POST.get('categoria_saida', '').strip()
        forma_pagamento_id = request.POST.get('forma_pagamento_saida', '').strip()
        status = request.POST.get('status_saida')
        data_vencimento = request.POST.get('data_vencimento_saida')
        data_lancamento_str = request.POST.get('data_lancamento_saida')

        if valor <= 0:
            raise ValueError("Valor da Saída deve ser maior que zero.")
        if not categoria_id or not forma_pagamento_id:
            raise ValueError("Categoria e Forma de Pagamento são obrigatórios para Saída.")

        categoria = Categoria.objects.get(pk=categoria_id)
        forma_pagamento = FormaPagamento.objects.get(pk=forma_pagamento_id)

        data_lancamento = (
            datetime.strptime(data_lancamento_str, '%Y-%m-%d').date()
            if data_lancamento_str else timezone.now().date()
        )

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
        return redirect('vendas_lancar')


# ===================================================================
# VIEW PRINCIPAL (UNIFICADA)
# ===================================================================
@login_required
@require_http_methods(["GET", "POST"])
def lancamento_vendas_view(request):
    """Página principal de lançamentos (Entrada e Saída)."""
    if request.method == 'POST':
        tipo_lancamento = request.POST.get('tipo_lancamento')

        if tipo_lancamento == 'ENTRADA':
            return salvar_venda(request)
        elif tipo_lancamento == 'SAIDA':
            return salvar_saida(request)
        else:
            return redirect('vendas_lancar')

    elif request.method == 'GET':
        data_atual = timezone.now().strftime('%Y-%m-%d')
        data_hora_atual = timezone.now().strftime('%Y-%m-%dT%H:%M')

        context = {
            'formas_pagamento': FormaPagamento.objects.all(),
            'categorias_saida': Categoria.objects.filter(tipo='S').order_by('nome'),
            'produtos': Produto.objects.all().order_by('nome'),
            'data_venda_default': data_hora_atual,
            'data_atual': data_atual
        }
        return render(request, 'vendas/lancamento_vendas.html', context)


# ===================================================================
# VIEW DE CONSULTA RÁPIDA (AJAX) — sem login obrigatório
# ===================================================================
def buscar_cliente_ajax(request):
    """Busca o cliente pelo ID OU nome e retorna o saldo de cashback e dívidas."""
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 1:
        return JsonResponse({'cliente_encontrado': False})

    if query.isdigit():
        try:
            cliente = Cliente.objects.get(pk=query)
            return JsonResponse({
                'cliente_encontrado': True,
                'id': cliente.id,
                'nome': str(cliente),
                'cashback': float(cliente.saldo_cashback),
                'divida': float(cliente.divida_total),
            })
        except Cliente.DoesNotExist:
            pass

    clientes_encontrados = Cliente.objects.filter(
        Q(nome__icontains=query) | Q(apelido__icontains=query)
    ).order_by('nome')[:10]

    if clientes_encontrados.exists():
        if len(clientes_encontrados) == 1:
            cliente = clientes_encontrados.first()
            data = {
                'cliente_encontrado': True,
                'id': cliente.id,
                'nome': str(cliente),
                'cashback': float(cliente.saldo_cashback),
                'divida': float(cliente.divida_total),
            }
        else:
            data = {
                'cliente_encontrado': True,
                'sugestoes': [{'id': c.id, 'nome': str(c)} for c in clientes_encontrados]
            }
    else:
        data = {
            'cliente_encontrado': False,
            'mensagem': 'Cliente não encontrado. Deseja cadastrar agora?',
            'nome_sugerido': query
        }

    return JsonResponse(data)
