from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Cliente
from .forms import ClienteForm


def home(request):
    return render(request, 'home.html')