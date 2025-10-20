from django import forms
from .models import Venda # Certifique-se de que Venda está importado

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        # Certifique-se de que 'data_venda' está na lista de campos
        fields = ['cliente', 'data_venda', 'valor_total', 'observacoes', 'itens'] 
        
        widgets = {
            # Adiciona o widget de Data e Hora
            'data_venda': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}, 
                # Define o formato esperado pelo widget 'datetime-local' do HTML5
                format='%Y-%m-%dT%H:%M' 
            ),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            # ... outros widgets conforme necessário
        }
    
    # Adiciona um valor inicial (default) à data da venda
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define a data_venda com o horário atual ao carregar o form,
        # para que o usuário precise apenas ajustar.
        from django.utils import timezone
        self.fields['data_venda'].initial = timezone.now().strftime('%Y-%m-%dT%H:%M')