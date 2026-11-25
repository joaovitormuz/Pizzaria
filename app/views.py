from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Cliente
from .forms import ClienteForm


def home(request):
    return render(request, 'home.html')

from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


def area_cliente(request):
    return render(request, 'areas/area_cliente.html')


def area_pizzaria(request):
    return render(request, 'areas/area_pizzaria.html')


def area_entregador(request):
    return render(request, 'areas/area_entregador.html')


def visao_geral(request):
    return render(request, 'areas/visao_geral.html')