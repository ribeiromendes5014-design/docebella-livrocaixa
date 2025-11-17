# financeiro/models.py
from django.db import models

class Categoria(models.Model):
    TIPO_CHOICES = [('E', 'Entrada'), ('S', 'Saída')]
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nome}"

class FormaPagamento(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Movimentacao(models.Model):
    STATUS_CHOICES = [('PAGO', 'Pago'), ('PENDENTE', 'Pendente')]
    TIPO_CHOICES = [('E', 'Entrada'), ('S', 'Saída')]

    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PAGO')
    data_lancamento = models.DateField()
    data_vencimento = models.DateField(null=True, blank=True)
    cliente_fornecedor = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} - {self.descricao}"

class ConfiguracaoCashback(models.Model):
    cashback_ativo = models.BooleanField(default=True, help_text="Marque para ativar o sistema de cashback.")
    percentual_cashback = models.DecimalField(max_digits=5, decimal_places=2, default=3.00, help_text="Percentual a ser gerado sobre o valor da venda (ex: 3.00 para 3%).")

    def __str__(self):
        return "Configurações de Cashback"