
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import Cliente, Pedido, Produto
from .forms import ClienteForm


# =====================================================
# PÁGINAS PRINCIPAIS
# =====================================================

def home(request):
    return render(request, 'home.html')



# =====================================================
# ÁREAS COM CONTROLE DE ACESSO
# =====================================================

@login_required
def area_cliente(request):
    if not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Acesso permitido somente para clientes.'
        )

    return render(request, 'areas/area_cliente.html')


@login_required
def area_pizzaria(request):
    if not request.user.is_staff:
        return HttpResponseForbidden(
            'Acesso permitido somente para funcionários autorizados.'
        )

    return render(request, 'areas/area_pizzaria.html')


@login_required
def area_entregador(request):
    if not hasattr(request.user, 'entregador'):
        return HttpResponseForbidden(
            'Acesso permitido somente para entregadores.'
        )

    return render(request, 'areas/area_entregador.html')


@login_required
def visao_geral(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden(
            'Acesso permitido somente para administradores.'
        )

    return render(request, 'areas/visao_geral.html')



# =====================================================
# CADASTRO PÚBLICO DE CLIENTES
# =====================================================

def cadastro_publico_cliente(request):
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
        'clientes/formulario.html',
        {
            'form': form,
            'titulo': 'Criar conta de cliente',
            'publico': True
        }
    )


# =====================================================
# VERIFICAÇÃO DE PERMISSÃO ADMINISTRATIVA
# =====================================================

def acesso_administrativo(user):
    return user.is_staff or user.is_superuser


# =====================================================
# LISTAR CLIENTES
# =====================================================

@login_required
def listar_clientes(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para acessar esta página.'
        )

    clientes = Cliente.objects.all()

    return render(
        request,
        'clientes/listar.html',
        {'clientes': clientes}
    )


# =====================================================
# CADASTRAR CLIENTE PELA PIZZARIA
# =====================================================

@login_required
def cadastrar_cliente(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para cadastrar clientes.'
        )

    if request.method == 'POST':
        form = ClienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm()

    return render(
        request,
        'clientes/formulario.html',
        {
            'form': form,
            'titulo': 'Cadastrar cliente'
        }
    )


# =====================================================
# EDITAR CLIENTE
# =====================================================

@login_required
def editar_cliente(request, pk):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para editar clientes.'
        )

    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)

    return render(
        request,
        'clientes/formulario.html',
        {
            'form': form,
            'titulo': 'Editar cliente'
        }
    )


# =====================================================
# EXCLUIR CLIENTE
# =====================================================

@login_required
def excluir_cliente(request, pk):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para excluir clientes.'
        )

    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('listar_clientes')

    return render(
        request,
        'clientes/confirmar_exclusao.html',
        {'cliente': cliente}
    )

# =====================================================
# CONSULTAR PEDIDOS DO CLIENTE
# =====================================================

@login_required
def meus_pedidos(request):
    if not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Esta funcionalidade é exclusiva para clientes.'
        )

    pedidos = Pedido.objects.filter(
        cliente=request.user.cliente
    ).order_by('-data_hora')

    return render(
        request,
        'clientes/meus_pedidos.html',
        {'pedidos': pedidos}
    )

# =====================================================
# PRODUTOS DISPONÍVEIS PARA O CLIENTE
# =====================================================

@login_required
def produtos_disponiveis(request):
    if not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Esta funcionalidade é exclusiva para clientes.'
        )

    produtos = Produto.objects.filter(
        disponibilidade=True
    ).order_by('nome')

    return render(
        request,
        'clientes/produtos.html',
        {'produtos': produtos}
    )
