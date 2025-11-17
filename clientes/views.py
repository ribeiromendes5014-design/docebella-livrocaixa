# clientes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Cliente, CashbackMovimento
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from vendas.models import Venda, FormaPagamento
from financeiro.models import Movimentacao, Categoria
import decimal
from django.db import transaction, models
from django.utils import timezone



# ==========================================================
# 1. LISTAR CLIENTES (banco de dados PostgreSQL)
# ==========================================================
def clientes_lista_view(request):
    """
    Lista todos os clientes cadastrados no banco de dados PostgreSQL.
    """
    clientes = Cliente.objects.all().order_by('nome')
    context = {"clientes": clientes}
    return render(request, "clientes/clientes_lista.html", context)


# ==========================================================
# 2. EXCLUIR CLIENTE
# ==========================================================
def excluir_cliente(request, cliente_id):
    if request.method == 'POST':
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'O cliente "{nome}" foi excluído com sucesso!')
    return redirect('clientes_lista')


# ==========================================================
# 3. DETALHE DO CLIENTE (usa banco)
# ==========================================================

def cliente_detalhe_view(request, pk):
    """
    Exibe informações completas de um cliente (busca no banco PostgreSQL),
    incluindo histórico de compras e movimentações de cashback.
    """
    cliente = get_object_or_404(Cliente, pk=pk)

    # Histórico de compras
    historico_compras = Venda.objects.filter(cliente=cliente).select_related('movimentacao_caixa').order_by('-data_venda')

    # Movimentações de cashback
    movimentos_cashback = CashbackMovimento.objects.filter(cliente=cliente).order_by('-data_movimento')

    # Formas de pagamento para o modal
    formas_pagamento = FormaPagamento.objects.all()

    context = {
        "cliente": cliente,
        "historico_compras": historico_compras,
        "movimentos_cashback": movimentos_cashback,
        "formas_pagamento": formas_pagamento,
    }

    return render(request, "clientes/cliente_detalhe.html", context)


@require_POST
def clientes_quitar_divida_view(request, pk):
    """
    Processa o formulário de quitação de dívida do modal.
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    
    try:
        valor_str = request.POST.get('valor', '0').replace(',', '.')
        valor_pago = decimal.Decimal(valor_str)
        forma_pagamento_id = request.POST.get('forma_pagamento')

        if not forma_pagamento_id:
            messages.error(request, "Forma de pagamento é obrigatória.")
            return redirect('cliente_detalhe', pk=cliente.pk)

        if valor_pago <= 0:
            messages.error(request, "O valor pago deve ser maior que zero.")
            return redirect('cliente_detalhe', pk=cliente.pk)
        
        forma_pagamento = get_object_or_404(FormaPagamento, pk=forma_pagamento_id)

        with transaction.atomic():
            # 1. Registra a entrada do dinheiro no caixa
            categoria_venda, _ = Categoria.objects.get_or_create(nome='Vendas', tipo='E')
            Movimentacao.objects.create(
                tipo='E',
                valor=valor_pago,
                descricao=f"Pagamento de dívida do cliente: {cliente.nome}",
                categoria=categoria_venda,
                forma_pagamento=forma_pagamento,
                status='PAGO',
                data_lancamento=timezone.now().date(),
                cliente_fornecedor=cliente
            )

            # 2. Lógica para abater o valor das dívidas (da mais antiga para a mais nova)
            dividas_abertas = cliente.divida_set.filter(pago=False).order_by('pk')
            valor_restante_a_pagar = valor_pago

            for divida in dividas_abertas:
                if valor_restante_a_pagar <= 0: break
                
                valor_a_abater = min(valor_restante_a_pagar, divida.valor_pendente)
                divida.valor_pendente -= valor_a_abater
                valor_restante_a_pagar -= valor_a_abater
                if divida.valor_pendente == 0:
                    divida.pago = True
                divida.save()
            
            # 3. Atualiza o saldo devedor consolidado no cliente
            # ⭐️ CORREÇÃO: Recalcula o total da dívida a partir da fonte da verdade (as dívidas restantes)
            novo_total_divida = cliente.divida_set.filter(pago=False).aggregate(total=models.Sum('valor_pendente'))['total'] or decimal.Decimal('0.00')
            cliente.divida_total_db = novo_total_divida
            cliente.save()

        messages.success(request, f"Pagamento de R$ {valor_pago:.2f} para {cliente.nome} registrado com sucesso!")

    except decimal.InvalidOperation:
        messages.error(request, "Valor de pagamento inválido.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao processar o pagamento: {e}")

    return redirect('cliente_detalhe', pk=cliente.pk)


@require_POST
def excluir_movimento_cashback_view(request, movimento_id):
    """
    Exclui uma movimentação de cashback e recalcula o saldo do cliente.
    """
    movimento = get_object_or_404(CashbackMovimento, pk=movimento_id)
    cliente = movimento.cliente

    try:
        with transaction.atomic():
            # Exclui a movimentação
            movimento.delete()

            # Recalcula o saldo de cashback do cliente a partir da fonte da verdade
            novo_saldo = cliente.cashbackmovimento_set.aggregate(total=models.Sum('valor'))['total'] or decimal.Decimal('0.00')
            cliente.saldo_cashback_db = novo_saldo
            cliente.save()

            messages.success(request, "Movimentação de cashback excluída e saldo do cliente atualizado com sucesso.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao excluir a movimentação: {e}")

    return redirect('cliente_detalhe', pk=cliente.pk)


@require_POST
def excluir_venda_view(request, venda_id):
    """
    Exclui uma Venda e reverte todas as operações associadas:
    - Restaura o estoque dos produtos.
    - Exclui movimentações de cashback e dívidas geradas.
    - Exclui a movimentação de caixa associada.
    - Recalcula os saldos do cliente.
    """
    venda = get_object_or_404(Venda, pk=venda_id)
    cliente = venda.cliente

    try:
        with transaction.atomic():
            # 1. Restaurar o estoque dos produtos vendidos
            for item in venda.itens.all():
                produto = item.produto
                produto.estoque += item.quantidade
                produto.save()

            # 2. Excluir a movimentação de caixa principal (se houver)
            if venda.movimentacao_caixa:
                venda.movimentacao_caixa.delete()
            
            # 3. Excluir a venda (isso irá deletar em cascata os VendaItem,
            #    CashbackMovimento e Divida, se configurado no modelo)
            venda.delete()

            # 4. Recalcular saldos do cliente para garantir consistência
            if cliente:
                # Recalcula saldo de cashback
                novo_saldo_cashback = cliente.cashbackmovimento_set.aggregate(total=models.Sum('valor'))['total'] or decimal.Decimal('0.00')
                cliente.saldo_cashback_db = novo_saldo_cashback

                # Recalcula saldo de dívidas
                novo_total_divida = cliente.divida_set.filter(pago=False).aggregate(total=models.Sum('valor_pendente'))['total'] or decimal.Decimal('0.00')
                cliente.divida_total_db = novo_total_divida
                
                cliente.save()

            messages.success(request, f"Venda #{venda_id} foi excluída com sucesso e todas as operações foram revertidas.")
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao excluir a venda: {e}")

    return redirect('cliente_detalhe', pk=cliente.pk) if cliente else redirect('clientes_lista')


# ==========================================================
# 4. CADASTRO RÁPIDO (AJAX) - salva no banco
# ==========================================================
@require_POST
@csrf_exempt
def cadastro_rapido_ajax(request):
    """
    Recebe os dados do modal de cadastro rápido e salva no banco PostgreSQL.
    """
    try:
        nome = request.POST.get("nome")
        sobrenome = request.POST.get("sobrenome")
        apelido = request.POST.get("apelido")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")

        if not nome:
            return JsonResponse({"sucesso": False, "mensagem": "Nome é obrigatório."}, status=400)

        # Cria o cliente direto no banco
        cliente = Cliente.objects.create(
            nome=nome,
            sobrenome=sobrenome,
            apelido=apelido,
            telefone=telefone,
            email=email,
        )

        return JsonResponse({
            "sucesso": True,
            "id": cliente.id,
            "nome": cliente.nome,
            "saldo_cashback": cliente.saldo_cashback,
            "divida_total": cliente.divida_total,
        })

    except Exception as e:
        return JsonResponse({"sucesso": False, "mensagem": f"Erro ao cadastrar: {e}"}, status=500)
