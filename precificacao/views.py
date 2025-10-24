# precificacao/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Produto

def precificacao_view(request):
    produtos = Produto.objects.all()

    # --- FILTRA APENAS OS PRODUTOS DO MÊS ATUAL ---
    hoje = timezone.now()
    produtos = produtos.filter(criado_em__year=hoje.year, criado_em__month=hoje.month)

    if request.method == "POST":
        nome = request.POST.get('nome')
        quantidade = int(request.POST.get('quantidade', 1))
        valor_pago = float(request.POST.get('valor_pago', 0))
        custo_extra = float(request.POST.get('custo_extra', 0))
        margem_lucro = request.POST.get('margem_lucro')
        valor_sugerido = request.POST.get('valor_sugerido')

        # --- CALCULA O CUSTO TOTAL UNITÁRIO ---
        custo_total = valor_pago + custo_extra

        # --- Se o usuário informou a margem de lucro (%), calcula o preço final ---
        if margem_lucro and not valor_sugerido:
            margem_lucro = float(margem_lucro)
            valor_final = custo_total * (1 + margem_lucro / 100)
        # --- Se o usuário informou o valor final sugerido, calcula a margem real ---
        elif valor_sugerido:
            valor_final = float(valor_sugerido)
            margem_lucro = ((valor_final - custo_total) / custo_total) * 100
        else:
            valor_final = custo_total
            margem_lucro = 0

        # --- Salva o produto ---
        Produto.objects.create(
            nome=nome,
            quantidade=quantidade,
            valor_pago=valor_pago,
            custo_extra=custo_extra,
            custo_total=custo_total,
            valor_final=valor_final,
            margem_lucro=margem_lucro,
        )

        return redirect('precificacao')

    context = {
        'produtos': produtos,
    }
    return render(request, 'precificacao/precificacao.html', context)
