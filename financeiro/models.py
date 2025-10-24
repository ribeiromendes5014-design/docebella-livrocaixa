# financeiro/models.py
from django.db import models

class Categoria(models.Model):
    """
    Categorias para classificar Entradas e Saídas (Ex: Aluguel, Salários, Venda).
    """
    TIPO_CATEGORIA = [
        ('E', 'Entrada'),
        ('S', 'Saída'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=1, choices=TIPO_CATEGORIA)
    
    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.nome}"
    
class FormaPagamento(models.Model):
    """
    Formas de pagamento (Pix, Cartão de Crédito, Dinheiro).
    """
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome

class Movimentacao(models.Model):
    """
    Registro principal do Fluxo de Caixa (Entradas e Saídas).
    """
    STATUS_MOV = [
        ('PAGO', 'Pago/Recebido'),
        ('PENDENTE', 'Pendente (Contas a Pagar/Receber)'),
        ('DIVIDA', 'Dívida/Inadimplência'),
    ]
    
    TIPO_MOV = [
        ('E', 'Entrada'),
        ('S', 'Saída'),
    ]
    
    tipo = models.CharField(max_length=1, choices=TIPO_MOV)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255)
    
    # Chaves Estrangeiras
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT, null=True, blank=True)
    
    # Datas
    data_lancamento = models.DateField(auto_now_add=True)
    data_vencimento = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_MOV, default='PAGO')

    def __str__(self):
        return f"{self.get_tipo_display()} R$ {self.valor} - {self.categoria.nome}"