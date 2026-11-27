
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone

from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from .models import Cliente, Pedido, Produto, ItemPedido
from .forms import (
    ClienteForm,
    AdicionarProdutoForm,
    ConfirmarPedidoForm
)
from .models import Cliente, Pedido, Produto, ItemPedido, Funcionario
from .forms import (
    ClienteForm,
    AdicionarProdutoForm,
    ConfirmarPedidoForm,
    FuncionarioForm,
    EntregadorForm,
    IngredienteForm,
    EstoqueForm,
    ReceitaForm,
    ProdutoForm
)

from .models import (
    Cliente,
    Pedido,
    Produto,
    ItemPedido,
    Funcionario,
    Entrega,
    Entregador,
    Ingrediente,
    Estoque,
    Receita,
    MovimentacaoEstoque,
    Pagamento,
    ProcessamentoPedido
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

                    Pagamento.objects.create(
                        pedido=pedido,
                        valor=pedido.preco_total,
                        metodo_pagamento=form.cleaned_data[
                            'metodo_pagamento'
                        ],
                        status_pagamento='Pendente'
                    )

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

        if novo_status not in status_validos:
            messages.error(request, 'Status inválido.')
            return redirect('listar_pedidos')

        try:
            with transaction.atomic():

                # Bloqueia o pedido durante a operação
                pedido = Pedido.objects.select_for_update().get(
                    pk=pk
                )

                # Baixa o estoque somente ao iniciar a preparação
                if (
                    novo_status == 'Em preparação'
                    and not pedido.estoque_baixado
                ):
                    quantidades_necessarias = {}

                    itens = pedido.itens.select_related(
                        'produto'
                    ).all()

                    if not itens.exists():
                        raise ValueError(
                            'O pedido não possui itens.'
                        )

                    # Calcula os ingredientes necessários
                    for item in itens:
                        receitas = Receita.objects.filter(
                            produto=item.produto
                        )

                        if not receitas.exists():
                            raise ValueError(
                                f'O produto "{item.produto.nome}" '
                                'não possui receita cadastrada.'
                            )

                        for receita in receitas:
                            ingrediente_id = receita.ingrediente_id

                            quantidade = (
                                receita.quantidade_medida
                                * item.quantidade
                            )

                            quantidades_necessarias[ingrediente_id] = (
                                quantidades_necessarias.get(
                                    ingrediente_id,
                                    Decimal('0')
                                ) + quantidade
                            )

                    # Bloqueia os registros de estoque
                    estoques = Estoque.objects.select_for_update().filter(
                        ingrediente_id__in=quantidades_necessarias.keys()
                    )

                    estoques_por_ingrediente = {
                        estoque.ingrediente_id: estoque
                        for estoque in estoques
                    }

                    # Verifica todos os ingredientes antes da baixa
                    for ingrediente_id, quantidade in quantidades_necessarias.items():

                        estoque = estoques_por_ingrediente.get(
                            ingrediente_id
                        )

                        if estoque is None:
                            ingrediente = Ingrediente.objects.get(
                                pk=ingrediente_id
                            )

                            raise ValueError(
                                f'Não existe estoque cadastrado para '
                                f'"{ingrediente.nome}".'
                            )

                        if estoque.quantidade_estoque < quantidade:
                            raise ValueError(
                                f'Estoque insuficiente de '
                                f'"{estoque.ingrediente.nome}". '
                                f'Necessário: {quantidade} '
                                f'{estoque.ingrediente.unidade_medida}. '
                                f'Disponível: {estoque.quantidade_estoque}.'
                            )

                    # Realiza a baixa dos ingredientes
                    for ingrediente_id, quantidade in quantidades_necessarias.items():

                        estoque = estoques_por_ingrediente[ingrediente_id]

                        estoque.quantidade_estoque -= quantidade

                        estoque.save(
                            update_fields=[
                                'quantidade_estoque',
                                'data_atualizacao'
                            ]
                        )

                        # Registra cada saída de estoque
                        MovimentacaoEstoque.objects.create(
                            ingrediente=estoque.ingrediente,
                            tipo='saida',
                            quantidade=quantidade,
                            descricao=(
                                f'Consumo do pedido '
                                f'#{pedido.id_pedido}'
                            ),
                            funcionario=(
                                request.user
                                if isinstance(request.user, Funcionario)
                                else None
                            )
                        )

                    pedido.estoque_baixado = True

                # Atualiza o status do pedido
                pedido.status = novo_status

                pedido.save(
                    update_fields=[
                        'status',
                        'estoque_baixado'
                    ]
                )

                # Gerencia o processamento do pedido
                if novo_status == 'Em preparação':

                    funcionario = Funcionario.objects.filter(
                        pk=request.user.pk
                    ).first()

                    if funcionario is None:
                        raise ValueError(
                            'O usuário responsável precisa estar '
                            'cadastrado como funcionário.'
                        )

                    processamento = ProcessamentoPedido.objects.filter(
                        pedido=pedido
                    ).first()

                    if processamento is None:
                        ProcessamentoPedido.objects.create(
                            pedido=pedido,
                            funcionario=funcionario,
                            data_inicio=timezone.now(),
                            status_preparacao='Em preparação'
                        )
                    else:
                        processamento.atualizarStatus(
                            'Em preparação'
                        )

                elif novo_status == 'Pronto':

                    processamento = ProcessamentoPedido.objects.filter(
                        pedido=pedido
                    ).first()

                    if processamento:
                        processamento.atualizarStatus(
                            'Finalizado'
                        )

            messages.success(
                request,
                f'Status do pedido #{pedido.id_pedido} atualizado!'
            )

        except ValueError as erro:
            messages.error(request, str(erro))

    return redirect('listar_pedidos')


# =====================================================
# Consultar Processamento do Pedido
# =====================================================
@login_required
def listar_processamentos(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    processamentos = ProcessamentoPedido.objects.select_related(
        'pedido',
        'funcionario'
    ).all().order_by('-data_inicio')

    return render(
        request,
        'processamentos/listar_processamentos.html',
        {'processamentos': processamentos}
    )
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

# =====================================================
# Cadastrar Produto
# =====================================================

@login_required
def cadastrar_produto(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    if request.method == 'POST':
        form = ProdutoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('listar_produtos')

    else:
        form = ProdutoForm()

    return render(
        request,
        'produtos/cadastrar.html',
        {'form': form}
    )

# =====================================================
# Editar Produto
# =====================================================

@login_required
def editar_produto(request, produto_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)

        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('listar_produtos')

    else:
        form = ProdutoForm(instance=produto)

    return render(
        request,
        'produtos/editar.html',
        {
            'form': form,
            'produto': produto
        }
    )

# =====================================================
# Excluir Produto
# =====================================================

@login_required
def excluir_produto(request, produto_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('listar_produtos')

    return render(
        request,
        'produtos/excluir.html',
        {'produto': produto}
    )

# =====================================================
# Listar Produto
# =====================================================
@login_required
def listar_produtos(request):
    produtos = Produto.objects.all().order_by('nome')

    return render(
        request,
        'produtos/listar.html',
        {'produtos': produtos}
    )

# =====================================================
# Cadastrar Ingredientes
# =====================================================
@login_required
def cadastrar_ingrediente(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    if request.method == 'POST':
        form = IngredienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente cadastrado com sucesso!')
            return redirect('listar_ingredientes')
    else:
        form = IngredienteForm()

    return render(request, 'estoque/cadastrar_ingrediente.html', {
        'form': form
    })




# =====================================================
# Listar Ingredientes
# =====================================================
@login_required
def listar_ingredientes(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    ingredientes = Ingrediente.objects.all().order_by('nome')

    return render(request, 'estoque/listar_ingredientes.html', {
        'ingredientes': ingredientes
    })

# =====================================================
# Editar Ingredientes
# =====================================================
@login_required
def editar_ingrediente(request, ingrediente_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id)

    if request.method == 'POST':
        form = IngredienteForm(request.POST, instance=ingrediente)

        if form.is_valid():
            form.save()
            messages.success(request, 'Ingrediente atualizado com sucesso!')
            return redirect('listar_ingredientes')
    else:
        form = IngredienteForm(instance=ingrediente)

    return render(request, 'estoque/editar_ingrediente.html', {
        'form': form,
        'ingrediente': ingrediente
    })

# =====================================================
# Excluir Ingredientes
# =====================================================

@login_required
def excluir_ingrediente(request, ingrediente_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    ingrediente = get_object_or_404(Ingrediente, pk=ingrediente_id)

    if request.method == 'POST':

        if hasattr(ingrediente, 'estoque') or ingrediente.receitas.exists():
         messages.warning(
         request,
         f'Não foi possível excluir o ingrediente "{ingrediente.nome}", '
         'pois ele está vinculado ao estoque ou a uma receita. '
         'Remova esses vínculos antes de tentar novamente.'
         )
         return redirect('listar_ingredientes')

        ingrediente.delete()

        messages.success(request, 'Ingrediente excluído com sucesso!')
        return redirect('listar_ingredientes')

    return render(request, 'estoque/excluir_ingrediente.html', {
        'ingrediente': ingrediente
    })

# =====================================================
# Listar Estoque
# =====================================================

@login_required
def listar_estoque(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    estoques = Estoque.objects.select_related(
        'ingrediente'
    ).all().order_by('ingrediente__nome')

    # Identifica os ingredientes com estoque baixo
    estoques_baixos = [
        estoque for estoque in estoques
        if estoque.verificarEstoque()
    ]

    return render(request, 'estoque/listar_estoque.html', {
        'estoques': estoques,
        'estoques_baixos': estoques_baixos,
    })

# =====================================================
# Cadastrar Estoque
# =====================================================
@login_required
def cadastrar_estoque(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    if request.method == 'POST':
        form = EstoqueForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Estoque cadastrado com sucesso!')
            return redirect('listar_estoque')
    else:
        form = EstoqueForm()

    return render(request, 'estoque/cadastrar_estoque.html', {
        'form': form
    })

# =====================================================
# Cadastrar Estoque
# =====================================================
@login_required
def editar_estoque(request, estoque_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    estoque = get_object_or_404(Estoque, pk=estoque_id)

    if request.method == 'POST':
        form = EstoqueForm(request.POST, instance=estoque)

        if form.is_valid():
            form.save()
            messages.success(request, 'Estoque atualizado com sucesso!')
            return redirect('listar_estoque')
    else:
        form = EstoqueForm(instance=estoque)

    return render(request, 'estoque/editar_estoque.html', {
        'form': form,
        'estoque': estoque
    })


# =====================================================
# Excluir Estoque
# =====================================================
@login_required
def excluir_estoque(request, estoque_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    estoque = get_object_or_404(Estoque, pk=estoque_id)

    if request.method == 'POST':
        estoque.delete()
        messages.success(request, 'Registro de estoque excluído com sucesso!')
        return redirect('listar_estoque')

    return render(request, 'estoque/excluir_estoque.html', {
        'estoque': estoque
    })

# =====================================================
# Listar Receitas
# =====================================================
@login_required
def listar_receitas(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    receitas = Receita.objects.select_related(
        'produto', 'ingrediente'
    ).all().order_by('produto__nome')

    return render(request, 'receitas/listar.html', {
        'receitas': receitas
    })

# =====================================================
# Cadastrar Receitas
# =====================================================
@login_required
def cadastrar_receita(request):
    produtos = Produto.objects.all().order_by('nome')
    ingredientes_unidades = {
    str(ingrediente.id_ingrediente): ingrediente.unidade_medida
    for ingrediente in Ingrediente.objects.all()
     }
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    from .forms import ReceitaFormSet

    if request.method == 'POST':
        produto_id = request.POST.get('produto')
        formset = ReceitaFormSet(request.POST)

        if formset.is_valid() and produto_id:
            produto = get_object_or_404(Produto, pk=produto_id)

            for form in formset:
                if form.cleaned_data:
                    ingrediente = form.cleaned_data['ingrediente']

                    receita, criada = Receita.objects.update_or_create(
                        produto=produto,
                        ingrediente=ingrediente,
                        defaults={
                            'unidade_medida': form.cleaned_data['unidade_medida'],
                            'quantidade_medida': form.cleaned_data['quantidade_medida'],
                        },
                    )

            messages.success(request, 'Receita cadastrada com sucesso!')
            return redirect('listar_receitas')

    else:
        formset = ReceitaFormSet()

    return render(request, 'receitas/cadastrar.html', {
    'produtos': produtos,
    'formset': formset,
    'ingredientes_unidades': ingredientes_unidades,
     })


# =====================================================
# Editar Receitas
# =====================================================
@login_required
def editar_receita(request, produto_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    from .forms import ReceitaFormSet
    from django.db import transaction

    produto = get_object_or_404(Produto, pk=produto_id)

    receitas = Receita.objects.filter(
        produto=produto
    ).select_related('ingrediente')

    if request.method == 'POST':
        formset = ReceitaFormSet(request.POST)

        if formset.is_valid():
            ingredientes_selecionados = []

            with transaction.atomic():
                for form in formset:
                    if form.cleaned_data:
                        ingrediente = form.cleaned_data.get('ingrediente')

                        if ingrediente:
                            ingredientes_selecionados.append(ingrediente.pk)

                            Receita.objects.update_or_create(
                                produto=produto,
                                ingrediente=ingrediente,
                                defaults={
                                    'unidade_medida': form.cleaned_data['unidade_medida'],
                                    'quantidade_medida': form.cleaned_data['quantidade_medida'],
                                }
                            )

                Receita.objects.filter(
                    produto=produto
                ).exclude(
                    ingrediente_id__in=ingredientes_selecionados
                ).delete()

            messages.success(request, 'Receita atualizada com sucesso!')
            return redirect('listar_receitas')

    else:
        dados_iniciais = [
            {
                'ingrediente': receita.ingrediente,
                'unidade_medida': receita.unidade_medida,
                'quantidade_medida': receita.quantidade_medida,
            }
            for receita in receitas
        ]

        formset = ReceitaFormSet(initial=dados_iniciais)

    return render(
        request,
        'receitas/editar.html',
        {
            'formset': formset,
            'produto': produto,
        },
    )

# =====================================================
# Excluir Receitas
# =====================================================
@login_required
def excluir_receita(request, produto_id):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        Receita.objects.filter(produto=produto).delete()

        messages.success(
            request,
            f'Receita de {produto.nome} excluída com sucesso!'
        )

        return redirect('listar_receitas')

    return render(
        request,
        'receitas/excluir.html',
        {'produto': produto}
    )

@login_required
def listar_pagamentos(request):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    pagamentos = Pagamento.objects.select_related(
        'pedido',
        'pedido__cliente'
    ).all().order_by('-id_pagamento')

    return render(
    request,
    'pagamentos/listar_pagamentos.html',
    {
        'pagamentos': pagamentos,
        'status_choices': Pagamento.STATUS_CHOICES,
    }
)


@login_required
def atualizar_status_pagamento(request, id_pagamento):
    if not acesso_administrativo(request.user):
        return HttpResponseForbidden('Acesso negado.')

    pagamento = get_object_or_404(
        Pagamento,
        id_pagamento=id_pagamento
    )

    if request.method == 'POST':
        novo_status = request.POST.get('status_pagamento')

        status_validos = [
            'Pendente',
            'Aprovado',
            'Recusado',
            'Estornado'
        ]

        if novo_status not in status_validos:
            messages.error(request, 'Status de pagamento inválido.')
            return redirect('listar_pagamentos')

        pagamento.status_pagamento = novo_status

        if novo_status == 'Aprovado':
            pagamento.data_pagamento = timezone.now()

        pagamento.save()

        messages.success(request, 'Pagamento atualizado com sucesso.')

    return redirect('listar_pagamentos')
