
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import ClienteForm


def home(request):
    return render(request, 'home.html')


def area_cliente(request):
    return render(request, 'areas/area_cliente.html')


def area_pizzaria(request):
    return render(request, 'areas/area_pizzaria.html')


def area_entregador(request):
    return render(request, 'areas/area_entregador.html')


def visao_geral(request):
    return render(request, 'areas/visao_geral.html')


def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Cadastro realizado com sucesso! Faça seu login.'
            )
            return redirect('login')

    else:
        form = ClienteForm()

    return render(
        request,
        'clientes/cadastro.html',
        {'form': form}
    )
