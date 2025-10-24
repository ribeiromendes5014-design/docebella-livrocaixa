# precificacao/admin.py
from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'quantidade',
        'valor_pago',
        'custo_extra',
        'custo_total',
        'valor_final',
        'margem_lucro',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('nome',)
    ordering = ('-created_at',)
