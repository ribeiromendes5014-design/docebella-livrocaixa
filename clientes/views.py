# clientes/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt 

from .models import Cliente, Divida, CashbackMovimento
from vendas.models import Venda 
from django.db.models import Q # Para buscas avançadas

# ===================================================================
# 1. VIEW DE LISTAGEM (URL: /clientes/)
# ===================================================================
def clientes_lista_view(request):
    """
    Lista todos os clientes com seus saldos de cashback e dívidas.
    """
    # Consulta todos os clientes e usa as @property para exibir os saldos
    clientes = Cliente.objects.all().order_by('nome')
    
    context = {
        'clientes': clientes
    }
    return render(request, 'clientes/clientes_lista.html', context)

# ===================================================================
# 2. VIEW DE DETALHE (URL: /clientes/<pk>/)
# ===================================================================
def cliente_detalhe_view(request, pk):
    """
    Exibe informações completas do cliente, histórico de compras, dívidas e cashback.
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # 2. Puxa todos os dados relacionados, otimizando o acesso ao banco
    dividas = cliente.divida_set.filter(pago=False).order_by('-data_vencimento')
    movimentos_cashback = cliente.cashbackmovimento_set.all().order_by('-data_movimento')
    historico_compras = Venda.objects.filter(cliente=cliente).select_related('movimentacao_caixa').order_by('-data_venda')
    
    context = {
        'cliente': cliente,
        'dividas': dividas,
        'movimentos_cashback': movimentos_cashback,
        'historico_compras': historico_compras,
    }
    
    return render(request, 'clientes/cliente_detalhe.html', context)

# ===================================================================
# 3. VIEW DE CADASTRO RÁPIDO (URL: /clientes/cadastrar-rapido/)
# ===================================================================
@require_POST
@csrf_exempt 
def cadastro_rapido_ajax(request):
    """
    Recebe os dados do modal de cadastro rápido (com campos adicionais) e cria um novo cliente.
    """
    try:
        # Campos Coletados do Formulário
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        apelido = request.POST.get('apelido')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        
        if not nome:
            return JsonResponse({'sucesso': False, 'mensagem': 'Nome é obrigatório.'}, status=400)
            
        # Cria o Cliente com todos os dados
        novo_cliente = Cliente.objects.create(
            nome=nome,
            sobrenome=sobrenome,
            apelido=apelido,
            telefone=telefone,
            email=email,
        )
        
        return JsonResponse({
            'sucesso': True,
            'id': novo_cliente.id,
            'nome': str(novo_cliente), 
            'saldo_cashback': float(novo_cliente.saldo_cashback),
            'divida_total': float(novo_cliente.divida_total),
        })

    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': f"Erro ao cadastrar: {e}"}, status=500)