
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

    # Cadastro de cliente
    path('cliente/cadastro/', views.cadastrar_cliente, name='cadastrar_cliente'),

    # Autenticação
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
]
