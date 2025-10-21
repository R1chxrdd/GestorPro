from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    Loja, Categoria, Fornecedor, Produto, 
    Estoque, MovimentacaoEstoque, Cliente, Venda, ItensVenda
)
from .forms import (
    LojaForm, UserRegisterForm, CategoriaForm, FornecedorForm, 
    ProdutoForm, MovimentacaoEstoqueForm, ClienteForm, VendaForm, ItemVendaForm
)




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


@staff_member_required
def lista_produtos(request):
    produtos = Produto.objects.select_related('estoque').all()
    return render(request, 'loja_app/produto_list.html', {'produtos': produtos})

@staff_member_required
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'loja_app/produto_form.html', {'form': form})

@staff_member_required
def editar_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'loja_app/produto_form.html', {'form': form})

@staff_member_required
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    if request.method == 'POST':
        produto.delete()
        return redirect('lista_produtos')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': produto, 'tipo': 'Produto'})

@staff_member_required
def atualizar_estoque(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    estoque = produto.estoque

    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST)
        if form.is_valid():
            quantidade = form.cleaned_data['quantidade']
            descricao = form.cleaned_data['descricao']
            estoque.quantidade += quantidade
            estoque.save()
            tipo_mov = 'ENTRADA' if quantidade > 0 else 'SAIDA'
            MovimentacaoEstoque.objects.create(
                produto=produto,
                quantidade=quantidade,
                tipo=tipo_mov,
                descricao=descricao
            )
            
            return redirect('lista_produtos')
    else:
        form = MovimentacaoEstoqueForm()

    context = {
        'form': form,
        'produto': produto,
        'estoque': estoque
    }
    return render(request, 'loja_app/atualizar_estoque.html', context)

@staff_member_required
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'loja_app/cliente_list.html', {'clientes': clientes})

@staff_member_required
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'loja_app/cliente_form.html', {'form': form, 'titulo': 'Cadastrar Novo Cliente'})

@staff_member_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'loja_app/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente'})

@staff_member_required
def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': cliente, 'tipo': 'Cliente'})

@staff_member_required
def lista_vendas(request):
    vendas = Venda.objects.all().order_by('-data_venda')
    return render(request, 'loja_app/venda_list.html', {'vendas': vendas})

@staff_member_required
@transaction.atomic # Garante que todas as operações de banco de dados aconteçam ou nenhuma aconteça
def registrar_venda(request):
    ItemVendaFormSet = formset_factory(ItemVendaForm, extra=1)

    if request.method == 'POST':
        venda_form = VendaForm(request.POST)
        item_formset = ItemVendaFormSet(request.POST)

        if venda_form.is_valid() and item_formset.is_valid():
            venda = venda_form.save(commit=False)
            venda.valor_total = 0
            venda.save()

            valor_total_venda = 0
            for form in item_formset:
                if form.cleaned_data:
                    produto = form.cleaned_data['produto']
                    quantidade = form.cleaned_data['quantidade']

                    # Verifica se há estoque suficiente
                    if produto.estoque.quantidade < quantidade:
                        messages.error(request, f"Estoque insuficiente para o produto: {produto.nome}. Disponível: {produto.estoque.quantidade}")
                        # transaction.atomic irá reverter a criação da venda
                        return redirect('registrar_venda')

                    # Cria o item da venda
                    item = form.save(commit=False)
                    item.venda = venda
                    item.preco_unitario = produto.preco_venda
                    item.save()

                    # Dá baixa no estoque
                    estoque = produto.estoque
                    estoque.quantidade -= quantidade
                    estoque.save()

                    # Atualiza o valor total
                    valor_total_venda += item.preco_unitario * item.quantidade

            # Salva o valor total na venda
            venda.valor_total = valor_total_venda
            venda.save()

            return redirect('lista_vendas')
    else:
        venda_form = VendaForm()
        item_formset = ItemVendaFormSet()

    context = {
        'venda_form': venda_form,
        'item_formset': item_formset,
        'titulo': 'Registrar Nova Venda'
    }
    return render(request, 'loja_app/venda_form.html', context)

@staff_member_required
@transaction.atomic
def cancelar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    
    if venda.status == 'CANCELADA':
        messages.error(request, 'Esta venda já foi cancelada.')
        return redirect('lista_vendas')

    if request.method == 'POST':
        # 1. Devolver itens ao estoque
        for item in venda.itens.all():
            estoque = item.produto.estoque
            estoque.quantidade += item.quantidade
            estoque.save()

            # 2. Registrar movimentação de estorno
            MovimentacaoEstoque.objects.create(
                produto=item.produto,
                quantidade=item.quantidade, # Quantidade positiva para entrada
                tipo='ENTRADA',
                descricao=f'Estorno por cancelamento da Venda #{venda.id}'
            )
        
        # 3. Atualizar o status da venda
        venda.status = 'CANCELADA'
        venda.save()

        messages.success(request, f'Venda #{venda.id} cancelada com sucesso. O estoque foi atualizado.')
        return redirect('lista_vendas')

    return render(request, 'loja_app/confirm_cancel.html', {'venda': venda})