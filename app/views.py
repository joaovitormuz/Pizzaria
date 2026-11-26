
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from django.db import transaction
from .models import Cliente, Pedido, Produto, ItemPedido
from .forms import (
    ClienteForm,
    AdicionarProdutoForm,
    ConfirmarPedidoForm
)
from .models import Cliente, Pedido, Produto, ItemPedido, Funcionario
from .forms import ClienteForm, AdicionarProdutoForm, ConfirmarPedidoForm, FuncionarioForm
from .forms import (
    ClienteForm,
    AdicionarProdutoForm,
    ConfirmarPedidoForm,
    FuncionarioForm,
    EntregadorForm
)

from .models import (
    Cliente,
    Pedido,
    Produto,
    ItemPedido,
    Funcionario,
    Entrega,
    Entregador
)


# Direcionamento por tipo de usuario


from django.contrib.auth.views import LoginView

class LoginPerfilView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        usuario = self.request.user

        if usuario.is_superuser:
            return '/visao-geral/'

        if hasattr(usuario, 'entregador'):
            return '/entregador/'

        if usuario.is_staff:
            return '/pizzaria/'

        if hasattr(usuario, 'cliente'):
            return '/cliente/'

        return '/'



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
# Cadastro Funcionario
# =====================================================

@login_required
def cadastrar_funcionario(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    if request.method == 'POST':
        form = FuncionarioForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário cadastrado com sucesso!')
            return redirect('area_pizzaria')
    else:
        form = FuncionarioForm()

    return render(request, 'funcionarios/formulario.html', {
        'form': form,
        'titulo': 'Cadastrar Funcionário'
    })

# =====================================================
# Cadastro Entregador
# =====================================================
@login_required
def cadastrar_entregador(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    if request.method == 'POST':
        form = EntregadorForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Entregador cadastrado com sucesso!'
            )
            return redirect('area_pizzaria')
    else:
        form = EntregadorForm()

    return render(request, 'entregadores/formulario.html', {
        'form': form,
        'titulo': 'Cadastrar Entregador'
    })


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
# =====================================================
# ADICIONAR PRODUTO AO CARRINHO
# =====================================================

@login_required
def adicionar_ao_carrinho(request, pk):
    if not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Esta funcionalidade é exclusiva para clientes.'
        )

    if request.method != 'POST':
        return redirect('produtos_disponiveis')

    produto = get_object_or_404(
        Produto,
        pk=pk,
        disponibilidade=True
    )

    form = AdicionarProdutoForm(request.POST)

    if form.is_valid():
        quantidade = form.cleaned_data['quantidade']

        carrinho = request.session.get('carrinho', {})

        produto_id = str(produto.pk)

        carrinho[produto_id] = (
            carrinho.get(produto_id, 0) + quantidade
        )

        request.session['carrinho'] = carrinho

        messages.success(
            request,
            f'{produto.nome} adicionado ao carrinho!'
        )

    return redirect('produtos_disponiveis')

 # =====================================================
# VISUALIZAR CARRINHO
# =====================================================

@login_required
def visualizar_carrinho(request):
    if not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Esta funcionalidade é exclusiva para clientes.'
        )

    carrinho = request.session.get('carrinho', {})

    produtos = []
    total = 0

    for produto_id, quantidade in carrinho.items():
        try:
            produto = Produto.objects.get(
                pk=produto_id,
                disponibilidade=True
            )
        except Produto.DoesNotExist:
            continue

        subtotal = produto.preco * quantidade

        produtos.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

        total += subtotal

    return render(
        request,
        'clientes/carrinho.html',
        {
            'produtos': produtos,
            'total': total
        }
    )

# =====================================================
# CONFIRMAR PEDIDO
# =====================================================

@login_required
def confirmar_pedido(request):
    if not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Esta funcionalidade é exclusiva para clientes.'
        )

    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('visualizar_carrinho')

    if request.method == 'POST':
        form = ConfirmarPedidoForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    pedido = Pedido.objects.create(
                        cliente=request.user.cliente,
                        tipo_entrega=form.cleaned_data['tipo_entrega'],
                        endereco_entrega=(
                            form.cleaned_data['endereco_entrega']
                            if form.cleaned_data['tipo_entrega'] == 'Entrega'
                            else ''
                        )
                    )

                    for produto_id, quantidade in carrinho.items():
                        produto = Produto.objects.get(
                            pk=produto_id,
                            disponibilidade=True
                        )

                        ItemPedido.objects.create(
                            pedido=pedido,
                            produto=produto,
                            quantidade=quantidade,
                            preco_unitario=produto.preco,
                            subtotal=produto.preco * quantidade
                        )

                    pedido.calcularTotal()

                    if pedido.tipo_entrega == 'Entrega':
                     Entrega.objects.create(
                     pedido=pedido,
                     endereco_entrega=pedido.endereco_entrega,
                     taxa_entrega=0
                     )

                del request.session['carrinho']

                messages.success(
                    request,
                    f'Pedido #{pedido.id_pedido} realizado com sucesso!'
                )

                return redirect('meus_pedidos')

            except Produto.DoesNotExist:
                messages.error(
                    request,
                    'Um dos produtos do carrinho não está mais disponível.'
                )
                return redirect('visualizar_carrinho')

    else:
        form = ConfirmarPedidoForm()

    return render(
        request,
        'clientes/confirmar_pedido.html',
        {'form': form}
    )

# =====================================================
# LISTAR PEDIDOS PARA A PIZZARIA
# =====================================================

@login_required
def listar_pedidos(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para visualizar os pedidos.'
        )

    pedidos = Pedido.objects.select_related(
        'cliente'
    ).prefetch_related(
        'itens__produto'
    ).order_by('-data_hora')

    return render(
    request,
    'pedidos/listar.html',
    {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES
    }
    )

# =====================================================
# ATUALIZAR STATUS DO PEDIDO
# =====================================================

@login_required
def atualizar_status_pedido(request, pk):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para atualizar pedidos.'
        )

    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == 'POST':
        novo_status = request.POST.get('status')

        status_validos = dict(Pedido.STATUS_CHOICES)

        if novo_status in status_validos:
            pedido.status = novo_status
            pedido.save(update_fields=['status'])

            messages.success(
                request,
                f'Status do pedido #{pedido.id_pedido} atualizado!'
            )
        else:
            messages.error(request, 'Status inválido.')

    return redirect('listar_pedidos')

# =====================================================
# CANCELAR PEDIDO
# =====================================================

@login_required
def cancelar_pedido(request, pk):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden(
            'Você não tem permissão para cancelar pedidos.'
        )

    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == 'POST':
        if pedido.status == 'Concluído':
            messages.error(
                request,
                'Não é possível cancelar um pedido concluído.'
            )
        elif pedido.status == 'Cancelado':
            messages.warning(
                request,
                'Este pedido já está cancelado.'
            )
        else:
            pedido.cancelarPedido()
            messages.success(
                request,
                f'Pedido #{pedido.id_pedido} cancelado com sucesso!'
            )

    return redirect('listar_pedidos')

# =====================================================
# listar entregas
# =====================================================
@login_required
def listar_entregas(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    entregas = Entrega.objects.select_related(
        'pedido',
        'pedido__cliente',
        'entregador'
    ).all().order_by('-id_entrega')

    return render(request, 'entregas/listar.html', {
    'entregas': entregas,
    'entregadores': Entregador.objects.filter(disponibilidade=True)
    })

# =====================================================
# Atribuir Entregas a entregadores
# =====================================================
@login_required
def atribuir_entregador(request, id_entrega):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    entrega = get_object_or_404(Entrega, pk=id_entrega)

    if request.method == 'POST':
        entregador_id = request.POST.get('entregador')

        entregador = get_object_or_404(
            Entregador,
            pk=entregador_id,
            disponibilidade=True
        )

        if entrega.status_entrega != 'Pendente':
            messages.error(
                request,
                'Não é possível alterar o entregador desta entrega.'
            )
            return redirect('listar_entregas')

        entrega.entregador = entregador
        entrega.save(update_fields=['entregador'])

        entregador.disponibilidade = False
        entregador.save(update_fields=['disponibilidade'])

        messages.success(
            request,
            'Entregador atribuído com sucesso!'
        )

        return redirect('listar_entregas')

    return redirect('listar_entregas')


# =====================================================
# Atualiza as disponibilidades do entregador
# =====================================================
@login_required
def atualizar_status_entrega(request, id_entrega):
    if not hasattr(request.user, 'entregador'):
        return HttpResponseForbidden('Acesso exclusivo para entregadores.')

    if request.method != 'POST':
        return redirect('area_entregador')

    entrega = get_object_or_404(
        Entrega,
        pk=id_entrega,
        entregador=request.user.entregador
    )

    novo_status = request.POST.get('status')

    if novo_status == 'Saiu para entrega':
        if entrega.status_entrega != 'Pendente':
            messages.error(request, 'Status inválido.')
            return redirect('area_entregador')

        entrega.status_entrega = 'Saiu para entrega'
        entrega.data_saida = timezone.now()
        entrega.pedido.status = 'Em entrega'

    elif novo_status == 'Entregue':
        if entrega.status_entrega != 'Saiu para entrega':
            messages.error(request, 'A entrega ainda não saiu.')
            return redirect('area_entregador')

        entrega.status_entrega = 'Entregue'
        entrega.data_entrega = timezone.now()
        entrega.pedido.status = 'Concluído'

        entregador = entrega.entregador
        entregador.disponibilidade = True
        entregador.save(update_fields=['disponibilidade'])

    else:
        messages.error(request, 'Status inválido.')
        return redirect('area_entregador')

    entrega.save()
    entrega.pedido.save(update_fields=['status'])

    messages.success(request, 'Status da entrega atualizado!')
    return redirect('area_entregador')

# =====================================================
# Entregadores podem visualizar as entregas atribuidas a eles
# =====================================================
@login_required
def minhas_entregas(request):
    if not hasattr(request.user, 'entregador'):
        return HttpResponseForbidden(
            'Esta funcionalidade é exclusiva para entregadores.'
        )

    entregas = Entrega.objects.filter(
        entregador=request.user.entregador
    ).select_related(
        'pedido',
        'pedido__cliente'
    ).order_by('-id_entrega')

    return render(request, 'entregadores/minhas_entregas.html', {
        'entregas': entregas
    })






