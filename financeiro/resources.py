# financeiro/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Movimentacao, Categoria, FormaPagamento
from decimal import Decimal

class MovimentacaoResource(resources.ModelResource):
    
    # Mapeamentos de Chaves Estrangeiras (usando a coluna do CSV)
    categoria = fields.Field(
        column_name='Cliente', 
        attribute='categoria',
        widget=ForeignKeyWidget(Categoria, 'nome') 
    )
    
    forma_pagamento = fields.Field(
        column_name='Forma de Pagamento', 
        attribute='forma_pagamento',
        widget=ForeignKeyWidget(FormaPagamento, 'nome')
    )

    # Mapeamento dos outros campos
    data_lancamento = fields.Field(column_name='Data', attribute='data_lancamento')
    valor = fields.Field(column_name='Valor', attribute='valor')
    
    # Campos que só existem para a conversão (usados no before_import_row)
    tipo_bruto = fields.Field(column_name='Tipo')
    status_bruto = fields.Field(column_name='Status')

    class Meta:
        model = Movimentacao
        fields = ( 
            'data_lancamento', 
            'tipo', 
            'valor', 
            'descricao', 
            'status', 
            'categoria', 
            'forma_pagamento', 
            'data_vencimento',
        )
        import_id_fields = ('data_lancamento', 'valor') 
        skip_unchanged = True


    def before_import_row(self, row, **kwargs):
        """
        Transforma e limpa os dados do CSV.
        """
        # 1. TRATAMENTO DO TIPO (Entrada/Saída)
        tipo_bruto = row.get('Tipo', '').strip().upper()
        row['tipo'] = 'E' if 'ENTRADA' in tipo_bruto else 'S' if 'SAÍDA' in tipo_bruto or 'SAIDA' in tipo_bruto else 'S'

        # 2. TRATAMENTO DO STATUS (Realizada/Pendente)
        status_bruto = row.get('Status', '').strip().upper()
        if 'REALIZADA' in status_bruto:
            row['status'] = 'PAGO'
        elif 'PENDENTE' in status_bruto:
            row['status'] = 'PENDENTE'
        else:
            row['status'] = 'PAGO' 

        # 3. TRATAMENTO DA CATEGORIA (Inferência a partir de Cliente/Tipo)
        categoria_bruta = row.get('Cliente', '').strip().lower()
        
        if 'compra' in categoria_bruta or 'mercadoria' in categoria_bruta:
            row['Cliente'] = 'CUSTO MERCADORIA' # AGORA EM UPPERCASE
        elif row['tipo'] == 'E':
            row['Cliente'] = 'VENDAS' # AGORA EM UPPERCASE
        elif row['tipo'] == 'S':
            row['Cliente'] = 'OUTRAS DESPESAS' # AGORA EM UPPERCASE

        # 4. TRATAMENTO DA FORMA DE PAGAMENTO (Padronização para UPPERCASE)
        forma_bruta = row.get('Forma de Pagamento', '').strip()
        # CRÍTICO: CONVERTE TUDO PARA UPPERCASE para garantir a correspondência
        row['Forma de Pagamento'] = forma_bruta.upper() if forma_bruta else 'DINHEIRO' 

        # 5. CRIAÇÃO DA DESCRIÇÃO E VALOR
        row['descricao'] = f"Transação: {row.get('Cliente', 'Avulso')} ({row.get('Loja', '')})"
        
        # Converte o valor para Decimal
        valor_bruto = row.get('Valor', '0')
        valor_limpo = valor_bruto.replace(',', '.').strip()
        
        try:
             row['Valor'] = Decimal(valor_limpo)
        except:
             raise ValueError(f"Valor inválido na coluna Valor: {valor_limpo}")