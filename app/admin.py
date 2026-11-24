
from django.contrib import admin
from .models import (
    Usuario,
    Cliente,
    Funcionario,
    Entregador,
    Pizzaria,
    Ingrediente,
    Estoque,
    Produto,
    Receita,
    Pedido,
    ItemPedido,
    Pagamento,
    ProcessamentoPedido,
    Entrega
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'numero_telefone')
    search_fields = ('nome', 'email')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'numero_telefone')
    search_fields = ('nome', 'email')


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'funcao', 'salario')
    list_filter = ('disponibilidade', 'funcao')
    search_fields = ('nome', 'email')


@admin.register(Entregador)
class EntregadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'email', 'taxa_entrega', 'disponibilidade')
    list_filter = ('disponibilidade',)
    search_fields = ('nome', 'email')


@admin.register(Pizzaria)
class PizzariaAdmin(admin.ModelAdmin):
    list_display = ('id_pizzaria', 'nome', 'email')


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('id_ingrediente', 'nome', 'tipo', 'unidade_medida')
    search_fields = ('nome',)


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'id_estoque',
        'ingrediente',
        'quantidade_estoque',
        'quantidade_minima'
    )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'id_produto',
        'nome',
        'categoria',
        'preco',
        'disponibilidade'
    )
    list_filter = ('categoria', 'disponibilidade')
    search_fields = ('nome',)


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = (
        'id_receita',
        'produto',
        'ingrediente',
        'quantidade_medida'
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id_pedido',
        'cliente',
        'data_hora',
        'status',
        'preco_total'
    )
    list_filter = ('status', 'tipo_entrega')
    search_fields = ('id_pedido', 'cliente__nome')


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id_item',
        'pedido',
        'produto',
        'quantidade',
        'subtotal'
    )


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        'id_pagamento',
        'pedido',
        'valor',
        'metodo_pagamento',
        'status_pagamento'
    )
    list_filter = ('status_pagamento',)


@admin.register(ProcessamentoPedido)
class ProcessamentoPedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id_processamento',
        'pedido',
        'funcionario',
        'status_preparacao'
    )
    list_filter = ('status_preparacao',)


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = (
        'id_entrega',
        'pedido',
        'entregador',
        'status_entrega',
        'taxa_entrega'
    )
    list_filter = ('status_entrega',)
