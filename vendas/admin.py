# vendas/admin.py
from django.contrib import admin
from .models import Produto, Venda, VendaItem

class VendaItemInline(admin.TabularInline):
    model = VendaItem
    extra = 0
    readonly_fields = ('produto', 'quantidade', 'valor_unitario', 'subtotal')
    can_delete = False

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'data_venda', 'valor_total', 'forma_pagamento')
    list_filter = ('data_venda', 'forma_pagamento')
    search_fields = ('cliente__nome', 'id')
    inlines = [VendaItemInline]

admin.site.register(Produto)