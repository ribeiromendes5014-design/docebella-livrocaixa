from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'valor_pago', 'custos_extras', 'margem_lucro', 'valor_sugerido', 'criado_em')
    search_fields = ('nome',)
    list_filter = ('criado_em',)
