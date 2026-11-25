
from django import forms
from .models import Cliente


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
            'referencia_pagamento'
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
