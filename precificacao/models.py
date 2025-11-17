from django.db import models
from django.utils import timezone

class Produto(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Produto")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Custo Unitário Base (R$)")
    custos_extras = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Custos Extras (R$)")
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Margem de Lucro (%)")
    valor_sugerido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Final Sugerido (R$)")
    criado_em = models.DateTimeField(auto_now_add=True)

    @property
    def custo_total(self):
        return self.valor_pago + self.custos_extras

    @property
    def preco_final_calculado(self):
        return self.custo_total * (1 + self.margem_lucro / 100)

    @property
    def margem_calculada(self):
        if self.valor_sugerido > 0:
            return ((self.valor_sugerido - self.custo_total) / self.custo_total) * 100
        return 0

    def __str__(self):
        return self.nome
