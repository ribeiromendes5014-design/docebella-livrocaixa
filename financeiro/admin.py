# financeiro/admin.py
from django.contrib import admin

# Importa os modelos
from .models import Categoria, FormaPagamento, Movimentacao

# Importa a biblioteca de importação/exportação (django-import-export)
from import_export.admin import ImportExportModelAdmin 
from .resources import MovimentacaoResource # Deve existir em financeiro/resources.py

# -----------------
# 1. ADMIN: Categoria (Entrada/Saída)
# -----------------
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nome',)

# -----------------
# 2. ADMIN: FormaPagamento (Dinheiro, Pix, Cartão)
# -----------------
@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

# -----------------
# 3. ADMIN: Movimentacao (Livro Caixa) - USANDO IMPORT/EXPORT
# -----------------
@admin.register(Movimentacao)
class MovimentacaoAdmin(ImportExportModelAdmin): # Herda do ImportExportModelAdmin
    resource_class = MovimentacaoResource # Associa a classe de recurso para CSV
    
    # Campos exibidos na lista
    list_display = ('id', 'data_lancamento', 'tipo', 'valor', 'categoria', 'status', 'data_vencimento')
    # Filtros laterais
    list_filter = ('tipo', 'status', 'categoria', 'data_lancamento')
    # Campos pesquisáveis
    search_fields = ('descricao', 'categoria__nome')
    
    # Campos que não podem ser editados após a criação
    readonly_fields = ('data_lancamento',) # Garante que a data de lançamento não seja alterada