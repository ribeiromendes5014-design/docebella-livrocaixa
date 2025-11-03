# precificacao/admin.py (CORRIGIDO)

from django.contrib import admin
from .models import Produto
from django.utils.html import format_html
from decimal import Decimal # Necessário para lidar com valores monetários

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # CORREÇÃO E033: Removido 'created_at'. Ordenando por 'nome' (assumindo que existe)
    ordering = ('nome',) 
    
    # Adicionando os métodos que serão criados abaixo
    list_display = (
        'nome',
        'quantidade',
        'valor_pago',
        'exibir_custo_extra',  # Novo método
        'exibir_custo_total',  # Novo método
        'exibir_valor_final',  # Novo método
        'margem_lucro',
        # 'data_criacao', # Se você tiver um campo chamado data_criacao, pode adicionar aqui.
    )
    
    # CORREÇÃO E116: Removido 'created_at'. Use um campo que existe, ex: 'nome'
    list_filter = ('nome',)
    
    search_fields = ('nome',)

    # Métodos para calcular e formatar os campos (necessário se não forem campos reais no model)

    def exibir_custo_extra(self, obj):
        # Substitua 'custo_extra_real' pelo nome do campo que armazena o custo extra no seu Produto
        # Se for um valor calculado, adicione a lógica de cálculo aqui.
        try:
            custo = obj.custo_extra_real # EX: obj.get_custo_extra()
        except AttributeError:
            custo = Decimal(0)
            
        return format_html('R$ {:,.2f}', custo)

    exibir_custo_extra.short_description = 'Custo Extra'
    exibir_custo_extra.admin_order_field = 'custo_extra_real' # Campo real para ordenação (ajustar)

    def exibir_custo_total(self, obj):
        # Lógica de cálculo: Exemplo simples
        custo = obj.valor_pago + obj.custo_extra_real # Ajuste os nomes dos campos aqui
        return format_html('R$ {:,.2f}', custo)

    exibir_custo_total.short_description = 'Custo Total'
    exibir_custo_total.admin_order_field = 'custo_total_real' # Campo real para ordenação (ajustar)

    def exibir_valor_final(self, obj):
        # Lógica de cálculo: Exemplo simples (Custo Total * (1 + Margem de Lucro))
        custo_total = obj.valor_pago + obj.custo_extra_real # Ajuste os nomes dos campos
        valor_final = custo_total * (Decimal(1) + (obj.margem_lucro / Decimal(100))) # Ajuste os campos
        return format_html('<span style="font-weight: bold;">R$ {:,.2f}</span>', valor_final)

    exibir_valor_final.short_description = 'Valor Final (Venda)'
    exibir_valor_final.admin_order_field = 'valor_final_real' # Campo real para ordenação (ajustar)