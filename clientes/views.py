# clientes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Cliente
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from vendas.models import Venda
from clientes.models import CashbackMovimento



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
from vendas.models import Venda
from clientes.models import CashbackMovimento

def cliente_detalhe_view(request, pk):
    """
    Exibe informações completas de um cliente (busca no banco PostgreSQL),
    incluindo histórico de compras e movimentações de cashback.
    """
    cliente = get_object_or_404(Cliente, pk=pk)

    # Histórico de compras
    historico_compras = Venda.objects.filter(cliente=cliente).order_by('-data_venda')

    # Movimentações de cashback
    movimentos_cashback = CashbackMovimento.objects.filter(cliente=cliente).order_by('-data_movimento')

    context = {
        "cliente": cliente,
        "saldo_cashback": cliente.saldo_cashback,
        "divida_total": cliente.divida_total,
        "historico_compras": historico_compras,
        "movimentos_cashback": movimentos_cashback,
    }

    return render(request, "clientes/cliente_detalhe.html", context)




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
