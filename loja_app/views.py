from django.shortcuts import render, redirect, get_object_or_404
from .models import Loja
from .forms import LojaForm, UserRegisterForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


# Dashboard 
@login_required
def home(request):
    return render(request, 'loja_app/home.html')



# Listar lojas 
@login_required
def lista_lojas(request):
    lojas = Loja.objects.all()
    return render(request, 'loja_app/loja_list.html', {'lojas': lojas})



# Cadastrar loja 
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



# Editar loja 
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



# Excluir loja 
@staff_member_required
def excluir_loja(request, id):
    loja = get_object_or_404(Loja, id=id)
    if request.method == 'POST':
        loja.delete()
        return redirect('lista_lojas')
    return render(request, 'loja_app/loja_confirm_delete.html', {'loja': loja})



def logout_view(request):
    logout(request)
    return redirect('login')



# View de Registro
def registrar_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Loga o usuário automaticamente após o registro
            messages.success(request, 'Registro bem-sucedido!')
            return redirect('dashboard') # Redireciona para o dashboard
    else:
        form = UserRegisterForm()
    return render(request, 'loja_app/register.html', {'form': form})


# View para a página "Sobre Nós"

def about_us_view(request):
    return render(request, 'loja_app/about_us.html')