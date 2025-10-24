# precificacao/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Produto

def precificacao_view(request):
    # Filtra apenas os produtos do mês atual
    hoje = timezone.now()
    produtos = Produto.objects.filter(criado_em__year=hoje.year, criado_em__month=hoje.month)

    if request.method == "POST":
        nome = request.POST.get('nome')
        quantidade = int(request.POST.get('quantidade', 1))
        valor_pago = float(request.POST.get('valor_pago', 0))
        custos_extras = float(request.POST.get('custos_extras', 0))
        margem_lucro = request.POST.get('margem_lucro')
        valor_sugerido = request.POST.get('valor_sugerido')

        # --- Cálculo do custo total unitário ---
        custo_total_unitario = valor_pago + custos_extras
        custo_total_geral = custo_total_unitario * quantidade

        # --- Se informou margem de lucro (%) ---
        if margem_lucro and not valor_sugerido:
            margem_lucro = float(margem_lucro)
            valor_final = custo_total_geral * (1 + margem_lucro / 100)

        # --- Se informou o valor final sugerido ---
        elif valor_sugerido:
            valor_final = float(valor_sugerido)
            margem_lucro = ((valor_final - custo_total_geral) / custo_total_geral) * 100

        # --- Caso nenhum dos dois ---
        else:
            valor_final = custo_total_geral
            margem_lucro = 0

        # --- Salva o produto ---
        Produto.objects.create(
            nome=nome,
            quantidade=quantidade,
            valor_pago=valor_pago,
            custos_extras=custos_extras,
            valor_sugerido=valor_final,
            margem_lucro=margem_lucro,
        )

        return redirect('precificacao')

    context = {
        'produtos': produtos,
    }
    return render(request, 'precificacao/precificacao.html', context)
