# vendas/models.py
from django.db import models
from clientes.models import Cliente
from financeiro.models import FormaPagamento, Movimentacao


class Produto(models.Model):
    """
    Cadastro de produtos ou serviços.
    """
    nome = models.CharField(max_length=100)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


class Venda(models.Model):
    """
    Registro da transação de venda.
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    data_venda = models.DateTimeField(auto_now_add=True)

    # Valores
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_cashback_utilizado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_cashback_gerado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Observações opcionais
    observacao = models.TextField(blank=True, null=True)

    # Relacionamentos com o Financeiro
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT)

    # A movimentação principal no fluxo de caixa (Entrada)
    movimentacao_caixa = models.ForeignKey(
        Movimentacao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='venda_entrada'
    )

    def __str__(self):
        return f"Venda #{self.id} - Cliente: {self.cliente.nome if self.cliente else 'Avulso'}"


class VendaItem(models.Model):
    """
    Itens de cada venda (produto, quantidade, valor unitário, subtotal).
    """
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} (Venda {self.venda.id})"
