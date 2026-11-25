from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Cliente
from .forms import ClienteForm


def home(request):
    return render(request, 'home.html')



def listar_clientes(request):
    clientes = Cliente.objects.all().order_by('nome')

    return render(request, 'clientes/listar.html', {
        'clientes': clientes
    })

@login_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm()

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': 'Cadastrar cliente'
    })


@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, pk=id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        if form.is_valid():
            # Na edição, não alteramos a senha do cliente.
            cliente = form.save(commit=False)
            cliente.save()

            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)
        form.fields.pop('senha')

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': 'Editar cliente'
    })


@login_required
def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, pk=id)

    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('listar_clientes')

    return render(request, 'clientes/confirmar_exclusao.html', {
        'cliente': cliente
    })