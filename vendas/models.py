# vendas/models.py
from django.db import models
from django.utils import timezone
from clientes.models import Cliente
from financeiro.models import FormaPagamento, Movimentacao

class Produto(models.Model):
    """
    Modelo para os produtos que são vendidos.
    """
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome

class Venda(models.Model):
    """
    Registro da transação de venda.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    
    # ⭐️ CORREÇÃO: Remove auto_now_add e usa 'default' para permitir que o valor seja sobrescrito.
    # Isso garante que a data/hora do formulário seja respeitada.
    data_venda = models.DateTimeField(default=timezone.now)

    # Valores
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_cashback_utilizado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_cashback_gerado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Relacionamentos
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT)
    movimentacao_caixa = models.OneToOneField(Movimentacao, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Outros
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Venda #{self.pk} - {self.cliente.nome if self.cliente else 'Avulso'}"

class VendaItem(models.Model):
    """
    Itens (produtos) que compõem uma Venda.
    """
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} na Venda #{self.venda.pk}"