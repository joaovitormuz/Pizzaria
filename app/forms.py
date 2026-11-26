
from django import forms
from .models import Cliente
from .models import Cliente, Funcionario, Entregador


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

class ConfirmarPedidoForm(forms.Form):

    TIPO_ENTREGA_CHOICES = [
        ('Entrega', 'Entrega'),
        ('Retirada', 'Retirada'),
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


