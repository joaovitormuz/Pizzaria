
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página inicial
    path('', views.home, name='home'),

    # Áreas do sistema
    path('cliente/', views.area_cliente, name='area_cliente'),
    path('pizzaria/', views.area_pizzaria, name='area_pizzaria'),
    path('entregador/', views.area_entregador, name='area_entregador'),
    path('visao-geral/', views.visao_geral, name='visao_geral'),

    # Cadastro público
    path(
        'cliente/cadastro/',
        views.cadastro_publico_cliente,
        name='cadastro_publico_cliente'
    ),

    # Gerenciamento administrativo de clientes
    path('clientes/', views.listar_clientes, name='listar_clientes'),
    path('clientes/novo/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path(
        'clientes/editar/<int:pk>/',
        views.editar_cliente,
        name='editar_cliente'
    ),
    path(
        'clientes/excluir/<int:pk>/',
        views.excluir_cliente,
        name='excluir_cliente'
    ),

    # Cadastrar Funcionario
    path(
    'funcionarios/cadastrar/',
    views.cadastrar_funcionario,
    name='cadastrar_funcionario'
    ),

    # Cadastrar Entregador
    path(
    'entregadores/cadastrar/',
    views.cadastrar_entregador,
    name='cadastrar_entregador'
),

    # Login e logout
    
        
     path(
    'login/',
    views.LoginPerfilView.as_view(),
    name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path(
    'cliente/meus-pedidos/',
    views.meus_pedidos,
    name='meus_pedidos'
    ),

    path(
    'cliente/produtos/',
    views.produtos_disponiveis,
    name='produtos_disponiveis'
    ),
    path(
    'cliente/carrinho/',
    views.visualizar_carrinho,
    name='visualizar_carrinho'
    ),

    path(
    'cliente/carrinho/adicionar/<int:pk>/',
    views.adicionar_ao_carrinho,
    name='adicionar_ao_carrinho'
    ),

    path(
    'cliente/confirmar-pedido/',
    views.confirmar_pedido,
    name='confirmar_pedido'
    ),

    path(
    'pizzaria/pedidos/',
    views.listar_pedidos,
    name='listar_pedidos'
    ),
    path(
    'pizzaria/pedidos/atualizar/<int:pk>/',
    views.atualizar_status_pedido,
    name='atualizar_status_pedido'
    ),
    
    path(
    'pizzaria/pedidos/cancelar/<int:pk>/',
    views.cancelar_pedido,
    name='cancelar_pedido'
    ),

    path(
    'entregas/',
    views.listar_entregas,
    name='listar_entregas'
    ),

   path(
    'entregas/<int:id_entrega>/atribuir/',
    views.atribuir_entregador,
    name='atribuir_entregador'
    ),

    path(
    'entregas/<int:id_entrega>/atualizar/',
    views.atualizar_status_entrega,
    name='atualizar_status_entrega'
    ),

    path(
    'minhas-entregas/',
    views.minhas_entregas,
    name='minhas_entregas'
    ),

    path(
    'ingredientes/cadastrar/',
    views.cadastrar_ingrediente,
    name='cadastrar_ingrediente'
    ),

    path(
    'ingredientes/',
    views.listar_ingredientes,
    name='listar_ingredientes'
   ),
   
   path(
    'estoque/',
    views.listar_estoque,
    name='listar_estoque'
    ),

    path(
    'estoque/cadastrar/',
    views.cadastrar_estoque,
    name='cadastrar_estoque'
    ),
    path(
    'receitas/',
    views.listar_receitas,
    name='listar_receitas'
    ),
    path(
    'receitas/cadastrar/',
    views.cadastrar_receita,
    name='cadastrar_receita'
    ),
    path(
    'receitas/<int:produto_id>/editar/',
    views.editar_receita,
    name='editar_receita'
    ),

    path(
    'receitas/<int:produto_id>/excluir/',
    views.excluir_receita,
    name='excluir_receita'
    ),
   
   path(
    'produtos/',
    views.listar_produtos,
    name='listar_produtos'
    ),

    path(
    'produtos/cadastrar/',
    views.cadastrar_produto,
    name='cadastrar_produto'
    ),

    path(
    'produtos/<int:produto_id>/editar/',
    views.editar_produto,
    name='editar_produto'
    ),

    path(
    'produtos/<int:produto_id>/excluir/',
    views.excluir_produto,
    name='excluir_produto'
    ),

    path(
    'ingredientes/<int:ingrediente_id>/editar/',
    views.editar_ingrediente,
    name='editar_ingrediente'
    ),

    path(
    'ingredientes/<int:ingrediente_id>/excluir/',
    views.excluir_ingrediente,
    name='excluir_ingrediente'
    ),

    path(
    'estoque/<int:estoque_id>/editar/',
    views.editar_estoque,
    name='editar_estoque'
    ),
    
    path(
    'estoque/<int:estoque_id>/excluir/',
    views.excluir_estoque,
    name='excluir_estoque'
    ),
    path(
    'pagamentos/',
    views.listar_pagamentos,
    name='listar_pagamentos'
    ),

    path(
    'pagamentos/<int:id_pagamento>/atualizar/',
    views.atualizar_status_pagamento,
    name='atualizar_status_pagamento'
    ),
    
]
