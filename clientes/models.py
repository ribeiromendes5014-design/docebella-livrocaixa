# clientes/models.py
from django.db import models
from django.db.models import Sum

class Cliente(models.Model):
    """
    Modelo base para o cadastro de clientes.
    """
    nome = models.CharField(max_length=150)
    # NOVOS CAMPOS ADICIONADOS:
    sobrenome = models.CharField(max_length=150, blank=True, null=True)
    apelido = models.CharField(max_length=100, blank=True, null=True)
    # Campos originais
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    
    # Campo calculado para acesso rápido (opcional, mas útil para consultas)
    @property
    def saldo_cashback(self):
        """ Retorna o saldo total de cashback do cliente. """
        saldo = self.cashbackmovimento_set.aggregate(total=Sum('valor'))['total']
        return saldo if saldo is not None else 0.00

    @property
    def divida_total(self):
        """ Retorna a soma de todas as dívidas pendentes do cliente. """
        total = self.divida_set.filter(pago=False).aggregate(total=Sum('valor_pendente'))['total']
        return total if total is not None else 0.00

    def __str__(self):
        """ Retorna o nome completo e apelido para melhor identificação. """
        partes = [self.nome]
        if self.sobrenome:
            partes.append(self.sobrenome)
        
        nome_completo = " ".join(partes)
        
        if self.apelido:
            return f"{nome_completo} ({self.apelido})"
        return nome_completo

class Divida(models.Model):
    """
    Rastreia dívidas (vendas pendentes sem data prevista ou atrasadas).
    """
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    valor_original = models.DecimalField(max_digits=10, decimal_places=2)
    valor_pendente = models.DecimalField(max_digits=10, decimal_places=2)
    data_vencimento = models.DateField(blank=True, null=True)
    pago = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Dívida de {self.cliente.nome} - R$ {self.valor_pendente}"
    
class CashbackMovimento(models.Model):
    """
    Rastreia todas as movimentações (geração e resgate) de cashback.
    """
    TIPO_MOVIMENTO = [
        ('G', 'Geração (Crédito)'),
        ('R', 'Resgate (Débito)'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_MOVIMENTO)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_movimento = models.DateTimeField(auto_now_add=True)
    
    # Relacionamento com o modelo Venda no App 'vendas'
    venda_referencia = models.ForeignKey(
        'vendas.Venda', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='movimentos_cashback'
    )
    
    def __str__(self):
        return f"{self.get_tipo_display()} de R$ {self.valor} para {self.cliente.nome}"