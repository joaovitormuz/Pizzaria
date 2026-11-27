
from django import forms
from django.forms import BaseFormSet, formset_factory
from django.core.exceptions import ValidationError
from .models import (
    Cliente, Funcionario, Entregador,
    Ingrediente, Estoque, Receita, Produto, MovimentacaoCaixa
)



class ClienteForm(forms.ModelForm):

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(),
        required=False
    )

    class Meta:
        model = Cliente
        fields = [
            'username',
            'nome',
            'email',
            'numero_telefone',
            'endereco',
        ]

    def clean_senha(self):
        senha = self.cleaned_data.get('senha')

        if not self.instance.pk and not senha:
            raise forms.ValidationError(
                'A senha é obrigatória para cadastrar um cliente.'
            )

        return senha

    def save(self, commit=True):
        cliente = super().save(commit=False)

        senha = self.cleaned_data.get('senha')

        if senha:
            cliente.set_password(senha)

        if commit:
            cliente.save()

        return cliente
    
class AdicionarProdutoForm(forms.Form):
 quantidade = forms.IntegerField(
  label='Quantidade',
    min_value=1,
 initial=1
)

class ProdutoForm(forms.ModelForm):

    class Meta:
        model = Produto
        fields = [
          'nome',
          'categoria',
          'descricao',
          'preco',
          'disponibilidade'
         ]

        labels = {
            'nome': 'Nome do produto',
            'categoria': 'Categoria',
            'descricao': 'Descrição',
            'preco': 'Preço',
            'disponibilidade': 'Disponibilidade'
        }

        widgets = {
            'descricao': forms.Textarea(attrs={
                'rows': 3
            }),
            'preco': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0'
            })
        }


class ConfirmarPedidoForm(forms.Form):

    TIPO_ENTREGA_CHOICES = [
        ('Entrega', 'Entrega'),
        ('Retirada', 'Retirada'),
    ]

    METODOS_PAGAMENTO = [
        ('Pix', 'Pix'),
        ('Dinheiro', 'Dinheiro'),
        ('Cartão de crédito', 'Cartão de crédito'),
        ('Cartão de débito', 'Cartão de débito'),
    ]

    tipo_entrega = forms.ChoiceField(
        label='Tipo de entrega',
        choices=TIPO_ENTREGA_CHOICES
    )

    endereco_entrega = forms.CharField(
        label='Endereço de entrega',
        max_length=255,
        required=False
    )

    metodo_pagamento = forms.ChoiceField(
        label='Método de pagamento',
        choices=METODOS_PAGAMENTO
    )

    def clean(self):
        cleaned_data = super().clean()

        tipo_entrega = cleaned_data.get('tipo_entrega')
        endereco = cleaned_data.get('endereco_entrega')

        if tipo_entrega == 'Entrega' and not endereco:
            self.add_error(
                'endereco_entrega',
                'Informe o endereço para entrega.'
            )

        return cleaned_data

class FuncionarioForm(forms.ModelForm):
    username = forms.CharField(
        label='Nome de usuário',
        max_length=150
    )

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput
    )

    class Meta:
        model = Funcionario
        fields = [
            'username',
            'nome',
            'email',
            'numero_telefone',
            'endereco',
            'salario',
            'disponibilidade',
            'funcao'
        ]

    def save(self, commit=True):
        funcionario = super().save(commit=False)
        funcionario.set_password(
            self.cleaned_data['senha']
        )
        funcionario.is_staff = True

        if commit:
            funcionario.save()

        return funcionario

    
class EntregadorForm(forms.ModelForm):
    username = forms.CharField(
        label='Nome de usuário',
        max_length=150
    )

    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput
    )

    class Meta:
        model = Entregador
        fields = [
            'username',
            'nome',
            'email',
            'numero_telefone',
            'endereco',
            'taxa_entrega',
            'disponibilidade'
        ]

    def save(self, commit=True):
        entregador = super().save(commit=False)
        entregador.set_password(self.cleaned_data['senha'])

        if commit:
            entregador.save()

        return entregador


class IngredienteForm(forms.ModelForm):

    class Meta:
        model = Ingrediente
        fields = [
            'nome',
            'tipo',
            'unidade_medida'
        ]

        labels = {
            'nome': 'Nome do ingrediente',
            'tipo': 'Tipo de Ingrediente',
            'unidade_medida': 'Unidade de medida'
        }


class EstoqueForm(forms.ModelForm):
    valor_pago = forms.DecimalField(
        label='Valor Pago (R$)',
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Valor total da compra'
        })
    )

    class Meta:
        model = Estoque
        fields = [
            'ingrediente',
            'quantidade_estoque',
            'quantidade_minima'
        ]


class ReceitaForm(forms.ModelForm):

    unidade_medida = forms.CharField(
        label='Unidade de medida',
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Receita
        fields = [
            'ingrediente',
            'unidade_medida',
            'quantidade_medida',
        ]
        labels = {
            'ingrediente': 'Ingrediente',
            'unidade_medida': 'Unidade de medida',
            'quantidade_medida': 'Quantidade utilizada',
        }
        widgets = {
            'quantidade_medida': forms.NumberInput(
                attrs={
                    'step': '0.001',
                    'min': '0',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['ingrediente'].required = False
        self.fields['quantidade_medida'].required = False

    def clean(self):
        cleaned_data = super().clean()

        ingrediente = cleaned_data.get('ingrediente')
        unidade = cleaned_data.get('unidade_medida')
        quantidade = cleaned_data.get('quantidade_medida')

        # Se não selecionar ingrediente, ignora a linha
        if not ingrediente:
            cleaned_data['unidade_medida'] = ''
            cleaned_data['quantidade_medida'] = None
            return cleaned_data

        # Exige a unidade de medida
        if not unidade:
            self.add_error(
                'unidade_medida',
                'A unidade de medida não foi preenchida.'
            )

        # Verifica se a unidade corresponde ao ingrediente
        elif unidade != ingrediente.unidade_medida:
            self.add_error(
                'unidade_medida',
                'A unidade deve corresponder à unidade do ingrediente.'
            )

        # Exige a quantidade
        if quantidade is None:
            self.add_error(
                'quantidade_medida',
                'Informe a quantidade.'
            )

        return cleaned_data


class BaseReceitaFormSet(BaseFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        ingredientes = [
            form.cleaned_data.get('ingrediente')
            for form in self.forms
            if form.cleaned_data and form.cleaned_data.get('ingrediente')
        ]

        if len(ingredientes) != len(set(ingredientes)):
            raise ValidationError(
                'Não selecione o mesmo ingrediente mais de uma vez.'
            )


ReceitaFormSet = formset_factory(
    ReceitaForm,
    formset=BaseReceitaFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
)


class MovimentacaoCaixaForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoCaixa
        fields = [
            'tipo',
            'descricao',
            'valor'
        ]

        labels = {
            'tipo': 'Tipo de movimentação',
            'descricao': 'Descrição',
            'valor': 'Valor (R$)'
        }

        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descreva a movimentação'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0,00'
            })
        }

    def clean_valor(self):
        valor = self.cleaned_data['valor']

        if valor <= 0:
            raise forms.ValidationError(
                'O valor deve ser maior que zero.'
            )

        return valor

