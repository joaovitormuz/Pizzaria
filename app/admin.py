
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Usuario,
    Cliente,
    Funcionario,
    Entregador,
    Pizzaria,
    Ingrediente,
    Estoque,
    MovimentacaoEstoque,
    Produto,
    Receita,
    Pedido,
    ItemPedido,
    Pagamento,
    ProcessamentoPedido,
    Entrega,
    CaixaPizzaria,
    MovimentacaoCaixa,
)


# Usuário e autenticação
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        'username',
        'nome',
        'email',
        'numero_telefone',
        'is_staff',
    )

    search_fields = ('username', 'nome', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações pessoais', {
            'fields': ('nome', 'email', 'numero_telefone', 'endereco')
        }),
        ('Permissões', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Datas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'nome',
                'email',
                'numero_telefone',
                'endereco',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
            ),
        }),
    )


# Clientes
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'email', 'numero_telefone')
    search_fields = ('username', 'nome', 'email')


# Funcionários
@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'funcao', 'salario', 'disponibilidade')
    search_fields = ('username', 'nome', 'funcao')
    list_filter = ('disponibilidade', 'funcao')


# Entregadores
@admin.register(Entregador)
class EntregadorAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'taxa_entrega', 'disponibilidade')
    search_fields = ('username', 'nome')
    list_filter = ('disponibilidade',)


# Pizzaria
@admin.register(Pizzaria)
class PizzariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'numero_telefone')
    search_fields = ('nome',)

# Caixa da pizzaria
@admin.register(CaixaPizzaria)
class CaixaPizzariaAdmin(admin.ModelAdmin):
    list_display = (
        'id_caixa',
        'pizzaria',
        'saldo_atual',
        'data_abertura',
        'data_atualizacao',
    )


# Movimentações do caixa
@admin.register(MovimentacaoCaixa)
class MovimentacaoCaixaAdmin(admin.ModelAdmin):
    list_display = (
        'id_movimentacao',
        'caixa',
        'tipo',
        'origem',
        'descricao',
        'valor',
        'data_movimentacao',
        'funcionario',
    )
    list_filter = ('tipo', 'origem', 'data_movimentacao')
    search_fields = ('descricao',)
    ordering = ('-data_movimentacao',)

# Ingredientes
@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'unidade_medida')
    search_fields = ('nome', 'tipo')


# Estoque
@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('ingrediente', 'quantidade_estoque',
                    'quantidade_minima', 'data_atualizacao')

# Movimentações de estoque
@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'id_movimentacao',
        'ingrediente',
        'tipo',
        'quantidade',
        'data_hora',
        'funcionario',
    )

    search_fields = ('ingrediente__nome', 'descricao')
    list_filter = ('tipo', 'data_hora')
    ordering = ('-data_hora',)


# Produtos
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponibilidade')
    search_fields = ('nome', 'categoria')
    list_filter = ('categoria', 'disponibilidade')


# Receitas
@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'ingrediente',
                    'quantidade_medida', 'unidade_medida')
    search_fields = ('produto__nome', 'ingrediente__nome')


# Pedidos
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'cliente', 'data_hora',
                    'status', 'preco_total', 'tipo_entrega')
    search_fields = ('cliente__nome',)
    list_filter = ('status', 'tipo_entrega', 'data_hora')


# Itens dos pedidos
@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('id_item', 'pedido', 'produto',
                    'quantidade', 'preco_unitario', 'subtotal')


# Pagamentos
@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('id_pagamento', 'pedido', 'valor',
                    'metodo_pagamento', 'status_pagamento')
    list_filter = ('metodo_pagamento', 'status_pagamento')


# Processamento dos pedidos
@admin.register(ProcessamentoPedido)
class ProcessamentoPedidoAdmin(admin.ModelAdmin):
    list_display = ('id_processamento', 'pedido', 'funcionario',
                    'status_preparacao', 'data_inicio', 'data_fim')
    list_filter = ('status_preparacao',)


# Entregas
@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('id_entrega', 'pedido', 'entregador',
                    'status_entrega', 'taxa_entrega')
    list_filter = ('status_entrega',)
