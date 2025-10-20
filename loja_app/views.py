from django.shortcuts import render, redirect, get_object_or_404
from .models import Loja, Categoria, Fornecedor
from .forms import LojaForm, UserRegisterForm, CategoriaForm, FornecedorForm 
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


def home(request):
    return render(request, 'loja_app/home.html')

def lista_lojas(request):
    lojas = Loja.objects.all()
    return render(request, 'loja_app/loja_list.html', {'lojas': lojas})

def logout_view(request):
    logout(request)
    return redirect('home')

def registrar_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registro bem-sucedido!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'loja_app/register.html', {'form': form})

def about_us_view(request):
    return render(request, 'loja_app/about_us.html')

@staff_member_required
def cadastrar_loja(request):
    if request.method == 'POST':
        form = LojaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_lojas')
    else:
        form = LojaForm()
    return render(request, 'loja_app/loja_form.html', {'form': form})

@staff_member_required
def editar_loja(request, id):
    loja = get_object_or_404(Loja, id=id)
    if request.method == 'POST':
        form = LojaForm(request.POST, instance=loja)
        if form.is_valid():
            form.save()
            return redirect('lista_lojas')
    else:
        form = LojaForm(instance=loja)
    return render(request, 'loja_app/loja_form.html', {'form': form})

@staff_member_required
def excluir_loja(request, id):
    loja = get_object_or_404(Loja, id=id)
    if request.method == 'POST':
        loja.delete()
        return redirect('lista_lojas')
    return render(request, 'loja_app/loja_confirm_delete.html', {'loja': loja})

@staff_member_required
def lista_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'loja_app/categoria_list.html', {'categorias': categorias})

@staff_member_required
def cadastrar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'loja_app/categoria_form.html', {'form': form})

@staff_member_required
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categorias')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': categoria, 'tipo': 'Categoria'})

@staff_member_required
def lista_fornecedores(request):
    fornecedores = Fornecedor.objects.all()
    return render(request, 'loja_app/fornecedor_list.html', {'fornecedores': fornecedores})

@staff_member_required
def cadastrar_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_fornecedores')
    else:
        form = FornecedorForm()
    return render(request, 'loja_app/fornecedor_form.html', {'form': form})

@staff_member_required
def editar_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            return redirect('lista_fornecedores')
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'loja_app/fornecedor_form.html', {'form': form})

@staff_member_required
def excluir_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    if request.method == 'POST':
        fornecedor.delete()
        return redirect('lista_fornecedores')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': fornecedor, 'tipo': 'Fornecedor'})