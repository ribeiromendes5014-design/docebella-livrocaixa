# clientes/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from core.github_storage import salvar_dados_json, ler_dados_json


# ==========================================================
# 1. LISTAR CLIENTES (usa dados do GitHub)
# ==========================================================
def clientes_lista_view(request):
    """
    Lista todos os clientes salvos no GitHub (data/clientes.json)
    """
    clientes = ler_dados_json("clientes")
    clientes = sorted(clientes, key=lambda c: c.get("nome", "").lower())

    context = {"clientes": clientes}
    return render(request, "clientes/clientes_lista.html", context)


# ==========================================================
# 2. DETALHE DO CLIENTE
# ==========================================================
def cliente_detalhe_view(request, pk):
    """
    Exibe informações completas de um cliente (busca no JSON).
    """
    clientes = ler_dados_json("clientes")

    # 🔧 Conversão para int antes da busca
    try:
        pk = int(pk)
    except ValueError:
        return JsonResponse({"erro": "ID inválido"}, status=400)

    cliente = next((c for c in clientes if c.get("id") == pk), None)

    if not cliente:
        return JsonResponse({"erro": "Cliente não encontrado"}, status=404)

    context = {"cliente": cliente}
    return render(request, "clientes/cliente_detalhe.html", context)



# ==========================================================
# 3. CADASTRO RÁPIDO (AJAX)
# ==========================================================
@require_POST
@csrf_exempt
def cadastro_rapido_ajax(request):
    """
    Recebe os dados do modal de cadastro rápido e salva no GitHub.
    """
    try:
        nome = request.POST.get("nome")
        sobrenome = request.POST.get("sobrenome")
        apelido = request.POST.get("apelido")
        telefone = request.POST.get("telefone")
        email = request.POST.get("email")

        if not nome:
            return JsonResponse({"sucesso": False, "mensagem": "Nome é obrigatório."}, status=400)

        # Lê a lista existente
        clientes = ler_dados_json("clientes")

        # Gera ID sequencial (baseado no último cliente)
        novo_id = (max([c.get("id", 0) for c in clientes]) + 1) if clientes else 1

        novo_cliente = {
            "id": novo_id,
            "nome": nome,
            "sobrenome": sobrenome,
            "apelido": apelido,
            "telefone": telefone,
            "email": email,
            "saldo_cashback": 0.0,
            "divida_total": 0.0,
        }

        # Adiciona e salva no GitHub
        clientes.append(novo_cliente)
        salvar_dados_json("clientes", clientes)

        return JsonResponse({
            "sucesso": True,
            "id": novo_id,
            "nome": nome,
            "saldo_cashback": 0.0,
            "divida_total": 0.0,
        })

    except Exception as e:
        return JsonResponse({"sucesso": False, "mensagem": f"Erro ao cadastrar: {e}"}, status=500)
