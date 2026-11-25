
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

    # Login e logout
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='usuarios/login.html'
        ),
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
]
