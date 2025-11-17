# financeiro/forms.py (CORRIGIDO)

from django import forms
from .models import Movimentacao, Categoria, FormaPagamento
# Nota: Categoria e FormaPagamento são importados, mas apenas Movimentacao é usada no ModelForm

class MovimentacaoForm(forms.ModelForm):
    """
    Formulário baseado no modelo Movimentacao para uso em views de Criação e Edição.
    """
    class Meta:
        model = Movimentacao
        # 'data_lancamento' é auto_now_add=True, então geralmente não é editado
        fields = [
            'tipo',
            'valor',
            'descricao',
            'categoria',
            'forma_pagamento',
            'data_vencimento',
            'status',
            'cliente_fornecedor', # <<< CAMPO ADICIONADO AQUI
        ]
        
        # Adiciona Widgets para melhorar a experiência do usuário (UX)
        widgets = {
            'data_vencimento': forms.DateInput(
                format='%Y-%m-%d', 
                attrs={'type': 'date'}
            ),
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }

    # Opcional: Filtra as categorias no formulário (útil se o form for para um tipo específico)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exemplo: Garante que a descrição seja um campo obrigatório
        self.fields['descricao'].required = True
        
        # Opcional: Adiciona a classe form-control para o campo cliente_fornecedor (se você não usou widget_tweaks)
        # self.fields['cliente_fornecedor'].widget.attrs.update({'class': 'form-control'})