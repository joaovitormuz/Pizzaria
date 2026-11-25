from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('cliente/', views.area_cliente, name='area_cliente'),
    path('pizzaria/', views.area_pizzaria, name='area_pizzaria'),
    path('entregador/', views.area_entregador, name='area_entregador'),
    path('visao-geral/', views.visao_geral, name='visao_geral'),
]