
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.db import transaction

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
    ProcessamentoPedido,
    CaixaPizzaria,
    MovimentacaoCaixa,
    Pizzaria,
)

from .forms import (
    ClienteForm,
    AdicionarProdutoForm,
    ConfirmarPedidoForm,
    FuncionarioForm,
    EntregadorForm,
    IngredienteForm,
    EstoqueForm,
    ReceitaForm,
    ProdutoForm,
    MovimentacaoCaixaForm,
    PizzariaForm,
)


# =====================================================
# VERIFICAÇÃO DE PERMISSÕES
# =====================================================

def acesso_administrativo(user):
    return user.is_authenticated and user.is_superuser


def usuario_tem_funcao(user, funcoes):
    if not user.is_authenticated:
        return False

    # Administrador possui acesso a todas as funcionalidades.
    if user.is_superuser:
        return True

    funcionario = Funcionario.objects.filter(pk=user.pk).first()

    if funcionario is None:
        return False

    return funcionario.funcao in funcoes


def acesso_negado(request):
    return render(request, 'acesso_negado.html')


# =====================================================
# DIRECIONAMENTO POR TIPO DE USUÁRIO
# =====================================================

class LoginPerfilView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        usuario = self.request.user

        if usuario.is_superuser:
            return '/'

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
    if not request.user.is_superuser and not hasattr(request.user, 'cliente'):
        return HttpResponseForbidden(
            'Acesso permitido somente para clientes.'
        )

    return render(request, 'areas/area_cliente.html')


@login_required
def area_pizzaria(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseForbidden(
            'Acesso permitido somente para funcionários autorizados.'
        )

    caixa = CaixaPizzaria.objects.select_related('pizzaria').first()

    return render(
        request,
        'areas/area_pizzaria.html',
        {'caixa': caixa}
    )


@login_required
def area_entregador(request):
    if not request.user.is_superuser and not hasattr(request.user, 'entregador'):
        return HttpResponseForbidden(
            'Acesso permitido somente para entregadores.'
        )

    return render(request, 'areas/area_entregador.html')


@login_required
def visao_geral(request):
    if not acesso_administrativo(request.user):
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
# FUNCIONÁRIOS
# =====================================================

@login_required
def cadastrar_funcionario(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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


@login_required
def editar_funcionario(request, id_funcionario):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    funcionario = get_object_or_404(Funcionario, pk=id_funcionario)

    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)

        if form.is_valid():
            form.save()
            messages.success(request, 'Funcionário atualizado com sucesso!')
            return redirect('area_pizzaria')
    else:
        form = FuncionarioForm(instance=funcionario)

    return render(request, 'funcionarios/formulario.html', {
        'form': form,
        'titulo': 'Editar Funcionário'
    })


@login_required
def listar_funcionarios(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    funcionarios = Funcionario.objects.all().order_by('nome')

    return render(request, 'funcionarios/listar.html', {
        'funcionarios': funcionarios
    })


# =====================================================
# ENTREGADORES - CADASTRO E GERENCIAMENTO
# =====================================================

@login_required
def cadastrar_entregador(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    if request.method == 'POST':
        form = EntregadorForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Entregador cadastrado com sucesso!')
            return redirect('area_pizzaria')
    else:
        form = EntregadorForm()

    return render(request, 'entregadores/formulario.html', {
        'form': form,
        'titulo': 'Cadastrar Entregador'
    })


@login_required
def editar_entregador(request, id_entregador):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    entregador = get_object_or_404(Entregador, pk=id_entregador)

    if request.method == 'POST':
        form = EntregadorForm(request.POST, instance=entregador)

        if form.is_valid():
            form.save()
            messages.success(request, 'Entregador atualizado com sucesso!')
            return redirect('area_pizzaria')
    else:
        form = EntregadorForm(instance=entregador)

    return render(request, 'entregadores/formulario.html', {
        'form': form,
        'titulo': 'Editar Entregador'
    })


@login_required
def listar_entregadores(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    entregadores = Entregador.objects.all().order_by('nome')

    return render(request, 'entregadores/listar.html', {
        'entregadores': entregadores
    })


# =====================================================
# CLIENTES - GERENCIAMENTO
# =====================================================

@login_required
def listar_clientes(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    clientes = Cliente.objects.all()

    return render(request, 'clientes/listar.html', {
        'clientes': clientes
    })


@login_required
def cadastrar_cliente(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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
def editar_cliente(request, pk):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('listar_clientes')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/formulario.html', {
        'form': form,
        'titulo': 'Editar cliente'
    })


@login_required
def excluir_cliente(request, pk):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente excluído com sucesso!')
        return redirect('listar_clientes')

    return render(request, 'clientes/confirmar_exclusao.html', {
        'cliente': cliente
    })


# =====================================================
# PEDIDOS DO CLIENTE
# =====================================================

@login_required
def meus_pedidos(request):
    if request.user.is_superuser:
        pedidos = Pedido.objects.select_related(
            'cliente'
        ).prefetch_related(
            'itens__produto'
        ).order_by('-data_hora')
    else:
        if not hasattr(request.user, 'cliente'):
            return acesso_negado(request)

        pedidos = Pedido.objects.filter(
            cliente=request.user.cliente
        ).order_by('-data_hora')

    return render(request, 'clientes/meus_pedidos.html', {
        'pedidos': pedidos
    })


# =====================================================
# PRODUTOS DISPONÍVEIS PARA CLIENTES
# =====================================================

@login_required
def produtos_disponiveis(request):
    if not request.user.is_superuser and not hasattr(request.user, 'cliente'):
        return acesso_negado(request)

    produtos = Produto.objects.filter(
        disponibilidade=True
    ).order_by('nome')

    return render(request, 'clientes/produtos.html', {
        'produtos': produtos
    })


# =====================================================
# CARRINHO
# =====================================================

@login_required
def adicionar_ao_carrinho(request, pk):
    if not request.user.is_superuser and not hasattr(request.user, 'cliente'):
        return acesso_negado(request)

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


@login_required
def visualizar_carrinho(request):
    if not request.user.is_superuser and not hasattr(request.user, 'cliente'):
        return acesso_negado(request)

    carrinho = request.session.get('carrinho', {})

    produtos = []
    total = Decimal('0')

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

    return render(request, 'clientes/carrinho.html', {
        'produtos': produtos,
        'total': total
    })


# =====================================================
# CONFIRMAR PEDIDO
# =====================================================

@login_required
def confirmar_pedido(request):
    if not request.user.is_superuser and not hasattr(request.user, 'cliente'):
        return acesso_negado(request)

    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('visualizar_carrinho')

    # O administrador precisa selecionar um cliente válido.
    cliente_pedido = None

    if request.user.is_superuser:
        cliente_id = request.POST.get('cliente') if request.method == 'POST' else None

        if cliente_id:
            cliente_pedido = get_object_or_404(Cliente, pk=cliente_id)
    else:
        cliente_pedido = request.user.cliente

    if request.method == 'POST':
        form = ConfirmarPedidoForm(request.POST)

        if form.is_valid():
            if cliente_pedido is None:
                messages.error(
                    request,
                    'Selecione um cliente para realizar o pedido.'
                )
                return redirect('visualizar_carrinho')

            try:
                with transaction.atomic():
                    pedido = Pedido.objects.create(
                        cliente=cliente_pedido,
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
                        metodo_pagamento=form.cleaned_data['metodo_pagamento'],
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

                if request.user.is_superuser:
                    return redirect('listar_pedidos')

                return redirect('meus_pedidos')

            except Produto.DoesNotExist:
                messages.error(
                    request,
                    'Um dos produtos do carrinho não está mais disponível.'
                )
                return redirect('visualizar_carrinho')

    else:
        form = ConfirmarPedidoForm()

    contexto = {'form': form}

    if request.user.is_superuser:
        contexto['clientes'] = Cliente.objects.all().order_by('nome')

    return render(request, 'clientes/confirmar_pedido.html', contexto)


# =====================================================
# LISTAR PEDIDOS PARA A PIZZARIA
# =====================================================

@login_required
def listar_pedidos(request):
    if not usuario_tem_funcao(request.user, ['Gerente', 'Atendente']):
        return acesso_negado(request)

    pedidos = Pedido.objects.select_related(
        'cliente'
    ).prefetch_related(
        'itens__produto'
    ).order_by('-data_hora')

    cozinheiros = Funcionario.objects.filter(
        funcao__in=['Pizzaiolo', 'Auxiliar de Cozinha']
    ).order_by('nome')

    return render(request, 'pedidos/listar.html', {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
        'cozinheiros': cozinheiros
    })


# =====================================================
# ATUALIZAR STATUS DO PEDIDO
# =====================================================

@login_required
def atualizar_status_pedido(request, pk):
    if not usuario_tem_funcao(
        request.user,
        ['Gerente', 'Atendente', 'Pizzaiolo', 'Auxiliar de Cozinha']
    ):
        return acesso_negado(request)

    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == 'POST':
        novo_status = request.POST.get('status')
        status_validos = dict(Pedido.STATUS_CHOICES)

        if novo_status not in status_validos:
            messages.error(request, 'Status inválido.')
            return redirect('listar_pedidos')

        if novo_status in ['Em preparação', 'Pronto']:
            funcoes_permitidas = [
                'Gerente',
                'Pizzaiolo',
                'Auxiliar de Cozinha'
            ]
        else:
            funcoes_permitidas = ['Gerente', 'Atendente']

        if not usuario_tem_funcao(request.user, funcoes_permitidas):
            return acesso_negado(request)

        try:
            with transaction.atomic():
                pedido = Pedido.objects.select_for_update().get(pk=pk)

                funcionario = Funcionario.objects.filter(
                    pk=request.user.pk
                ).first()

                processamento = ProcessamentoPedido.objects.filter(
                    pedido=pedido
                ).first()

                funcionario_responsavel = None

                if novo_status in ['Em preparação', 'Concluído']:
                    funcionario_id = request.POST.get(
                        'funcionario_responsavel'
                    )

                    if not funcionario_id:
                        raise ValueError(
                            'Selecione o cozinheiro responsável pelo pedido.'
                        )

                    funcionario_responsavel = get_object_or_404(
                        Funcionario,
                        pk=funcionario_id,
                        funcao__in=[
                            'Pizzaiolo',
                            'Auxiliar de Cozinha'
                        ]
                    )

                    if novo_status == 'Em preparação' and processamento:
                        raise ValueError(
                            'Este pedido já possui um processamento registrado.'
                        )

                if (
                    novo_status == 'Em preparação'
                    and not pedido.estoque_baixado
                ):
                    quantidades_necessarias = {}

                    itens = pedido.itens.select_related('produto').all()

                    if not itens.exists():
                        raise ValueError('O pedido não possui itens.')

                    for item in itens:
                        receitas = Receita.objects.filter(
                            produto=item.produto
                        )

                        for receita in receitas:
                            ingrediente_id = receita.ingrediente_id

                            quantidade = (
                                receita.quantidade_medida * item.quantidade
                            )

                            quantidades_necessarias[ingrediente_id] = (
                                quantidades_necessarias.get(
                                    ingrediente_id,
                                    Decimal('0')
                                ) + quantidade
                            )

                    estoques = Estoque.objects.select_for_update().filter(
                        ingrediente_id__in=quantidades_necessarias.keys()
                    )

                    estoques_por_ingrediente = {
                        estoque.ingrediente_id: estoque
                        for estoque in estoques
                    }

                    for ingrediente_id, quantidade in quantidades_necessarias.items():
                        estoque = estoques_por_ingrediente.get(ingrediente_id)

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

                    for ingrediente_id, quantidade in quantidades_necessarias.items():
                        estoque = estoques_por_ingrediente[ingrediente_id]

                        estoque.quantidade_estoque -= quantidade
                        estoque.save(update_fields=[
                            'quantidade_estoque',
                            'data_atualizacao'
                        ])

                        MovimentacaoEstoque.objects.create(
                            ingrediente=estoque.ingrediente,
                            tipo='saida',
                            quantidade=quantidade,
                            descricao=f'Consumo do pedido #{pedido.id_pedido}',
                            funcionario=funcionario
                        )

                    pedido.estoque_baixado = True

                pedido.status = novo_status
                pedido.save(update_fields=['status', 'estoque_baixado'])

                if novo_status == 'Em preparação':
                    ProcessamentoPedido.objects.create(
                        pedido=pedido,
                        funcionario=funcionario_responsavel,
                        data_inicio=timezone.now(),
                        status_preparacao='Em preparação'
                    )

                elif novo_status == 'Concluído':
                    if processamento is None:
                        agora = timezone.now()

                        ProcessamentoPedido.objects.create(
                            pedido=pedido,
                            funcionario=funcionario_responsavel,
                            data_inicio=agora,
                            data_fim=agora,
                            status_preparacao='Finalizado'
                        )
                    else:
                        processamento.atualizarStatus('Finalizado')

                elif novo_status == 'Pronto':
                    if processamento:
                        processamento.atualizarStatus('Finalizado')

            messages.success(
                request,
                f'Status do pedido #{pedido.id_pedido} atualizado!'
            )

        except ValueError as erro:
            messages.error(request, str(erro))

        except Funcionario.DoesNotExist:
            messages.error(
                request,
                'O cozinheiro selecionado não foi encontrado.'
            )

    return redirect('listar_pedidos')


# =====================================================
# CONSULTAR PROCESSAMENTOS
# =====================================================

@login_required
def listar_processamentos(request):
    if not usuario_tem_funcao(
        request.user,
        ['Gerente', 'Pizzaiolo', 'Auxiliar de Cozinha']
    ):
        return acesso_negado(request)

    processamentos = ProcessamentoPedido.objects.select_related(
        'pedido',
        'funcionario'
    ).all().order_by('-data_inicio')

    return render(request, 'processamentos/listar_processamentos.html', {
        'processamentos': processamentos
    })


# =====================================================
# CANCELAR PEDIDO
# =====================================================

@login_required
def cancelar_pedido(request, pk):
    if not usuario_tem_funcao(request.user, ['Gerente', 'Atendente']):
        return acesso_negado(request)

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
# LISTAR ENTREGAS
# =====================================================

@login_required
def listar_entregas(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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
# ATRIBUIR ENTREGADOR
# =====================================================

@login_required
def atribuir_entregador(request, id_entrega):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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


# =====================================================
# ATUALIZAR STATUS DA ENTREGA
# =====================================================

@login_required
def atualizar_status_entrega(request, id_entrega):
    administrador = request.user.is_superuser
    entregador_usuario = getattr(request.user, 'entregador', None)

    # Entregadores só podem atualizar suas próprias entregas.
    # Administradores podem atualizar qualquer entrega.
    if not administrador and entregador_usuario is None:
        return acesso_negado(request)

    if request.method != 'POST':
        if administrador:
            return redirect('listar_entregas')
        return redirect('area_entregador')

    if administrador:
        entrega = get_object_or_404(Entrega, pk=id_entrega)
    else:
        entrega = get_object_or_404(
            Entrega,
            pk=id_entrega,
            entregador=entregador_usuario
        )

    novo_status = request.POST.get('status')

    if novo_status == 'Saiu para entrega':
        if entrega.status_entrega != 'Pendente':
            messages.error(request, 'Status inválido.')
            return redirect(
                'listar_entregas' if administrador else 'area_entregador'
            )

        entrega.status_entrega = 'Saiu para entrega'
        entrega.data_saida = timezone.now()
        entrega.pedido.status = 'Em entrega'

    elif novo_status == 'Entregue':
        if entrega.status_entrega != 'Saiu para entrega':
            messages.error(request, 'A entrega ainda não saiu.')
            return redirect(
                'listar_entregas' if administrador else 'area_entregador'
            )

        entrega.status_entrega = 'Entregue'
        entrega.data_entrega = timezone.now()
        entrega.pedido.status = 'Concluído'

        # Libera o entregador, caso exista um associado.
        entregador = entrega.entregador

        if entregador:
            entregador.disponibilidade = True
            entregador.save(update_fields=['disponibilidade'])

    else:
        messages.error(request, 'Status inválido.')
        return redirect(
            'listar_entregas' if administrador else 'area_entregador'
        )

    entrega.save()
    entrega.pedido.save(update_fields=['status'])

    messages.success(request, 'Status da entrega atualizado!')

    if administrador:
        return redirect('listar_entregas')

    return redirect('area_entregador')


# =====================================================
# ENTREGAS ATRIBUÍDAS AO ENTREGADOR
# =====================================================

@login_required
def minhas_entregas(request):
    if request.user.is_superuser:
        entregas = Entrega.objects.all()
    else:
        if not hasattr(request.user, 'entregador'):
            return acesso_negado(request)

        entregas = Entrega.objects.filter(
            entregador=request.user.entregador
        )

    entregas = entregas.select_related(
        'pedido',
        'pedido__cliente',
        'entregador'
    ).order_by('-id_entrega')

    return render(request, 'entregadores/minhas_entregas.html', {
        'entregas': entregas
    })


# =====================================================
# PRODUTOS
# =====================================================

@login_required
def cadastrar_produto(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    if request.method == 'POST':
        form = ProdutoForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('listar_produtos')
    else:
        form = ProdutoForm()

    return render(request, 'produtos/cadastrar.html', {
        'form': form
    })


@login_required
def editar_produto(request, produto_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)

        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('listar_produtos')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'produtos/editar.html', {
        'form': form,
        'produto': produto
    })


@login_required
def excluir_produto(request, produto_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('listar_produtos')

    return render(request, 'produtos/excluir.html', {
        'produto': produto
    })


@login_required
def listar_produtos(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    produtos = Produto.objects.all().order_by('nome')

    return render(request, 'produtos/listar.html', {
        'produtos': produtos
    })


# =====================================================
# INGREDIENTES
# =====================================================

@login_required
def cadastrar_ingrediente(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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


@login_required
def listar_ingredientes(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    ingredientes = Ingrediente.objects.all().order_by('nome')

    return render(request, 'estoque/listar_ingredientes.html', {
        'ingredientes': ingredientes
    })


@login_required
def editar_ingrediente(request, ingrediente_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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


@login_required
def excluir_ingrediente(request, ingrediente_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

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
# ESTOQUE
# =====================================================

@login_required
def listar_estoque(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    estoques = Estoque.objects.select_related(
        'ingrediente'
    ).all().order_by('ingrediente__nome')

    estoques_baixos = [
        estoque for estoque in estoques
        if estoque.verificarEstoque()
    ]

    return render(request, 'estoque/listar_estoque.html', {
        'estoques': estoques,
        'estoques_baixos': estoques_baixos
    })


@login_required
def cadastrar_estoque(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    if request.method == 'POST':
        form = EstoqueForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    ingrediente = form.cleaned_data['ingrediente']
                    quantidade = form.cleaned_data['quantidade_estoque']
                    valor_pago = form.cleaned_data['valor_pago']

                    if quantidade <= 0:
                        raise ValueError(
                            'A quantidade adquirida deve ser maior que zero.'
                        )

                    if valor_pago <= 0:
                        raise ValueError(
                            'O valor pago deve ser maior que zero.'
                        )

                    caixa = CaixaPizzaria.objects.select_for_update().first()

                    if caixa is None:
                        raise ValueError(
                            'Não existe um caixa cadastrado para a pizzaria.'
                        )

                    if valor_pago > caixa.saldo_atual:
                        raise ValueError(
                            'Saldo insuficiente para realizar esta compra.'
                        )

                    estoque = Estoque.objects.select_for_update().filter(
                        ingrediente=ingrediente
                    ).first()

                    if estoque:
                        estoque.quantidade_estoque += quantidade
                        estoque.quantidade_minima = (
                            form.cleaned_data['quantidade_minima']
                        )
                        estoque.save()
                    else:
                        estoque = form.save(commit=False)
                        estoque.save()

                    funcionario = Funcionario.objects.filter(
                        pk=request.user.pk
                    ).first()

                    MovimentacaoEstoque.objects.create(
                        ingrediente=ingrediente,
                        tipo='entrada',
                        quantidade=quantidade,
                        valor_pago=valor_pago,
                        descricao='Compra e reposição de estoque.',
                        funcionario=funcionario
                    )

                    MovimentacaoCaixa.objects.create(
                        caixa=caixa,
                        tipo='Saida',
                        origem='Compra',
                        descricao=f'Compra de estoque: {ingrediente.nome}',
                        valor=valor_pago,
                        funcionario=funcionario
                    )

                    caixa.saldo_atual -= valor_pago
                    caixa.save(update_fields=[
                        'saldo_atual',
                        'data_atualizacao'
                    ])

                messages.success(
                    request,
                    'Estoque atualizado e compra registrada no caixa!'
                )
                return redirect('listar_estoque')

            except ValueError as erro:
                messages.error(request, str(erro))
    else:
        form = EstoqueForm()

    return render(request, 'estoque/cadastrar_estoque.html', {
        'form': form
    })


@login_required
def editar_estoque(request, estoque_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    estoque = get_object_or_404(Estoque, pk=estoque_id)

    if request.method == 'POST':
        form = EstoqueForm(request.POST, instance=estoque)

        if form.is_valid():
            try:
                with transaction.atomic():
                    valor_pago = form.cleaned_data['valor_pago']
                    quantidade_nova = form.cleaned_data['quantidade_estoque']

                    if quantidade_nova < 0:
                        raise ValueError(
                            'A quantidade não pode ser negativa.'
                        )

                    if valor_pago < 0:
                        raise ValueError(
                            'O valor pago não pode ser negativo.'
                        )

                    caixa = CaixaPizzaria.objects.select_for_update().first()

                    if caixa is None:
                        raise ValueError(
                            'Não existe um caixa cadastrado para a pizzaria.'
                        )

                    if valor_pago > caixa.saldo_atual:
                        raise ValueError(
                            'Saldo insuficiente para realizar esta compra.'
                        )

                    estoque = Estoque.objects.select_for_update().get(
                        pk=estoque_id
                    )

                    estoque.ingrediente = form.cleaned_data['ingrediente']
                    estoque.quantidade_estoque = quantidade_nova
                    estoque.quantidade_minima = (
                        form.cleaned_data['quantidade_minima']
                    )
                    estoque.save()

                    funcionario = Funcionario.objects.filter(
                        pk=request.user.pk
                    ).first()

                    MovimentacaoEstoque.objects.create(
                        ingrediente=estoque.ingrediente,
                        tipo='ajuste',
                        quantidade=quantidade_nova,
                        valor_pago=valor_pago,
                        descricao='Ajuste de estoque com registro de compra.',
                        funcionario=funcionario
                    )

                    MovimentacaoCaixa.objects.create(
                        caixa=caixa,
                        tipo='Saida',
                        origem='Compra',
                        descricao=f'Ajuste de estoque: {estoque.ingrediente.nome}',
                        valor=valor_pago,
                        funcionario=funcionario
                    )

                    caixa.saldo_atual -= valor_pago
                    caixa.save(update_fields=[
                        'saldo_atual',
                        'data_atualizacao'
                    ])

                messages.success(
                    request,
                    'Estoque atualizado e compra registrada no caixa!'
                )
                return redirect('listar_estoque')

            except ValueError as erro:
                messages.error(request, str(erro))
    else:
        form = EstoqueForm(instance=estoque)

    return render(request, 'estoque/editar_estoque.html', {
        'form': form,
        'estoque': estoque
    })


@login_required
def excluir_estoque(request, estoque_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    estoque = get_object_or_404(Estoque, pk=estoque_id)

    if request.method == 'POST':
        estoque.delete()
        messages.success(
            request,
            'Registro de estoque excluído com sucesso!'
        )
        return redirect('listar_estoque')

    return render(request, 'estoque/excluir_estoque.html', {
        'estoque': estoque
    })


# =====================================================
# RECEITAS
# =====================================================

@login_required
def listar_receitas(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    receitas = Receita.objects.select_related(
        'produto',
        'ingrediente'
    ).all().order_by('produto__nome')

    return render(request, 'receitas/listar.html', {
        'receitas': receitas
    })


@login_required
def cadastrar_receita(request):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    produtos = Produto.objects.all().order_by('nome')

    ingredientes_unidades = {
        str(ingrediente.id_ingrediente): ingrediente.unidade_medida
        for ingrediente in Ingrediente.objects.all()
    }

    from .forms import ReceitaFormSet

    if request.method == 'POST':
        produto_id = request.POST.get('produto')
        formset = ReceitaFormSet(request.POST)

        if formset.is_valid() and produto_id:
            produto = get_object_or_404(Produto, pk=produto_id)

            for form in formset:
                if form.cleaned_data:
                    ingrediente = form.cleaned_data['ingrediente']

                    Receita.objects.update_or_create(
                        produto=produto,
                        ingrediente=ingrediente,
                        defaults={
                            'unidade_medida': form.cleaned_data['unidade_medida'],
                            'quantidade_medida': form.cleaned_data['quantidade_medida'],
                        }
                    )

            messages.success(request, 'Receita cadastrada com sucesso!')
            return redirect('listar_receitas')
    else:
        formset = ReceitaFormSet()

    return render(request, 'receitas/cadastrar.html', {
        'produtos': produtos,
        'formset': formset,
        'ingredientes_unidades': ingredientes_unidades
    })


@login_required
def editar_receita(request, produto_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    from .forms import ReceitaFormSet

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
                'quantidade_medida': receita.quantidade_medida
            }
            for receita in receitas
        ]

        formset = ReceitaFormSet(initial=dados_iniciais)

    return render(request, 'receitas/editar.html', {
        'formset': formset,
        'produto': produto
    })


@login_required
def excluir_receita(request, produto_id):
    if not usuario_tem_funcao(request.user, ['Gerente']):
        return acesso_negado(request)

    produto = get_object_or_404(Produto, pk=produto_id)

    if request.method == 'POST':
        Receita.objects.filter(produto=produto).delete()

        messages.success(
            request,
            f'Receita de {produto.nome} excluída com sucesso!'
        )

        return redirect('listar_receitas')

    return render(request, 'receitas/excluir.html', {
        'produto': produto
    })


# =====================================================
# PAGAMENTOS
# =====================================================

@login_required
def listar_pagamentos(request):
    if not usuario_tem_funcao(request.user, ['Gerente', 'Caixa']):
        return acesso_negado(request)

    pagamentos = Pagamento.objects.select_related(
        'pedido',
        'pedido__cliente'
    ).all().order_by('-id_pagamento')

    return render(request, 'pagamentos/listar_pagamentos.html', {
        'pagamentos': pagamentos,
        'status_choices': Pagamento.STATUS_CHOICES
    })


@login_required
def atualizar_status_pagamento(request, id_pagamento):
    if not usuario_tem_funcao(request.user, ['Gerente', 'Caixa']):
        return acesso_negado(request)

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


# =====================================================
# GERENCIAR PIZZARIA
# =====================================================

@login_required
def gerenciar_pizzaria(request):
    if not acesso_administrativo(request.user):
        return acesso_negado(request)

    pizzaria = Pizzaria.objects.first()

    if request.method == 'POST':
        form = PizzariaForm(request.POST, instance=pizzaria)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Dados da pizzaria atualizados com sucesso!'
            )
            return redirect('gerenciar_pizzaria')
    else:
        form = PizzariaForm(instance=pizzaria)

    return render(request, 'pizzaria/gerenciar.html', {
        'form': form,
        'pizzaria': pizzaria
    })


# =====================================================
# CAIXA DA PIZZARIA
# =====================================================

@login_required
def consultar_caixa(request):
    if not usuario_tem_funcao(request.user, ['Gerente', 'Caixa']):
        return acesso_negado(request)

    caixa = CaixaPizzaria.objects.select_related('pizzaria').first()

    movimentacoes = []

    if caixa:
        movimentacoes = (
            MovimentacaoCaixa.objects.filter(caixa=caixa)
            .select_related('funcionario', 'pedido')
            .order_by('-data_movimentacao')
        )

    return render(request, 'caixa/consultar.html', {
        'caixa': caixa,
        'movimentacoes': movimentacoes
    })


@login_required
def registrar_movimentacao_caixa(request):
    if not usuario_tem_funcao(request.user, ['Gerente', 'Caixa']):
        return acesso_negado(request)

    caixa = CaixaPizzaria.objects.first()

    if caixa is None:
        messages.error(request, 'Não existe um caixa cadastrado.')
        return redirect('consultar_caixa')

    if request.method == 'POST':
        form = MovimentacaoCaixaForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    caixa = CaixaPizzaria.objects.select_for_update().get(
                        pk=caixa.pk
                    )

                    movimentacao = form.save(commit=False)
                    movimentacao.caixa = caixa
                    movimentacao.origem = 'Manual'
                    movimentacao.funcionario = Funcionario.objects.filter(
                        pk=request.user.pk
                    ).first()

                    if movimentacao.tipo == 'Saida':
                        if movimentacao.valor > caixa.saldo_atual:
                            raise ValueError(
                                'Saldo insuficiente para esta retirada.'
                            )

                        caixa.saldo_atual -= movimentacao.valor
                    else:
                        caixa.saldo_atual += movimentacao.valor

                    movimentacao.save()

                    caixa.save(update_fields=[
                        'saldo_atual',
                        'data_atualizacao'
                    ])

                messages.success(
                    request,
                    'Movimentação registrada com sucesso!'
                )
                return redirect('consultar_caixa')

            except ValueError as erro:
                messages.error(request, str(erro))

    else:
        form = MovimentacaoCaixaForm()

    return render(request, 'caixa/registrar_movimentacao.html', {
        'form': form
    })
