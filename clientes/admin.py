# clientes/admin.py
from django.contrib import admin
from .models import Cliente, Divida, CashbackMovimento
from vendas.models import Venda # Para usar no Detalhe do Cliente

# -----------------
# Inlines (Visualização dentro do Cliente)
# -----------------
class DividaInline(admin.TabularInline):
    model = Divida
    extra = 0
    can_delete = False
    readonly_fields = ('valor_pendente', 'data_vencimento')
    verbose_name_plural = 'Dívidas em Aberto'
    
class CashbackMovimentoInline(admin.TabularInline):
    model = CashbackMovimento
    extra = 0
    can_delete = False
    readonly_fields = ('tipo', 'valor', 'data_movimento', 'venda_referencia')
    verbose_name_plural = 'Histórico de Cashback'

class VendaInline(admin.TabularInline):
    model = Venda
    extra = 0
    can_delete = False
    readonly_fields = ('data_venda', 'valor_total', 'valor_cashback_gerado', 'forma_pagamento')
    verbose_name_plural = 'Histórico de Vendas'
    
# -----------------
# Admin Principal para Cliente
# -----------------
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'apelido', 'telefone', 'saldo_cashback_display', 'divida_total_display')
    search_fields = ('nome', 'sobrenome', 'apelido', 'telefone')
    
    # Adiciona as visualizações de dados relacionados na página de detalhes
    inlines = [DividaInline, CashbackMovimentoInline, VendaInline]
    
    # Campos em grupo para melhor visualização
    fieldsets = (
        (None, {
            'fields': ('nome', 'sobrenome', 'apelido')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
    )

    # Funções customizadas para exibição na lista
    def saldo_cashback_display(self, obj):
        return f"R$ {obj.saldo_cashback:.2f}"
    saldo_cashback_display.short_description = 'Cashback (R$)'
    
    def divida_total_display(self, obj):
        return f"R$ {obj.divida_total:.2f}"
    divida_total_display.short_description = 'Dívidas (R$)'
    
# -----------------
# Registro Simples dos Movimentos (se desejar ver no admin)
# -----------------
# @admin.register(Divida)
# class DividaAdmin(admin.ModelAdmin):
#     list_display = ('cliente', 'valor_pendente', 'pago')

# @admin.register(CashbackMovimento)
# class CashbackMovimentoAdmin(admin.ModelAdmin):
#     list_display = ('cliente', 'valor', 'tipo', 'data_movimento')