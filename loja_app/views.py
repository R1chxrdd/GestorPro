import json
from django.core.exceptions import FieldDoesNotExist
from django.db import models as django_models
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.db import transaction, IntegrityError
from django.db.models import Prefetch
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

# Importação de todos os Models
from .models import (
    Loja, Categoria, Fornecedor, Produto, 
    Estoque, MovimentacaoEstoque, Cliente, Venda, ItensVenda
)

# Importação de todos os Forms
from .forms import (
    LojaForm, UserRegisterForm, CategoriaForm, FornecedorForm, 
    ProdutoForm, MovimentacaoEstoqueForm, ClienteForm, VendaForm, ItemVendaForm
)

def _is_json_request(request):
    content_type = request.META.get('CONTENT_TYPE', '')
    return 'application/json' in content_type


def _load_json_payload(request):
    try:
        raw_body = request.body.decode('utf-8').strip()
    except UnicodeDecodeError as exc:
        raise ValueError('Corpo da requisição inválido.') from exc

    if not raw_body:
        return {}

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ValueError('JSON inválido.') from exc

    if not isinstance(payload, dict):
        raise ValueError('O corpo da requisição deve ser um objeto JSON.')

    return payload


def _update_instance_from_data(instance, data, allowed_fields):
    """Atualiza ``instance`` com dados parciais ignorando valores ``None``."""

    if not data:
        return []

    meta = instance._meta
    updated_fields = []

    for field_name, value in data.items():
        if field_name not in allowed_fields or value is None:
            continue

        try:
            field = meta.get_field(field_name)
        except FieldDoesNotExist:
            continue

        if isinstance(field, django_models.ForeignKey):
            related_model = field.remote_field.model
            if value is None:
                continue
            if isinstance(value, related_model):
                related_instance = value
            else:
                try:
                    related_instance = related_model.objects.get(pk=value)
                except (related_model.DoesNotExist, ValueError, TypeError) as exc:
                    raise ValueError(
                        f'{related_model.__name__} com id "{value}" não encontrado.'
                    ) from exc
            value = related_instance
        else:
            try:
                value = field.to_python(value)
            except Exception as exc:  # pragma: no cover - conversão protegida
                raise ValueError(
                    f'Valor inválido para o campo "{field.verbose_name}".'
                ) from exc

        setattr(instance, field_name, value)
        if field_name not in updated_fields:
            updated_fields.append(field_name)

    if updated_fields:
        instance.save(update_fields=updated_fields)

    return updated_fields

# ------------------------------
# VIEWS GERAIS
# ------------------------------

def home(request):
    return render(request, 'loja_app/home.html')

def about_us_view(request):
    return render(request, 'loja_app/about_us.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def registrar_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cliente.objects.create(user=user, nome=user.username)
            login(request, user)
            messages.success(request, 'Registro bem-sucedido!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'loja_app/register.html', {'form': form})


# ------------------------------
# LOJAS
# ------------------------------

@login_required
def lista_lojas(request):
    lojas = Loja.objects.all()
    return render(request, 'loja_app/loja_list.html', {'lojas': lojas})

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
    allowed_fields = ['nome', 'endereco', 'telefone', 'email']

    if request.method in ('PUT', 'PATCH') or _is_json_request(request):
        try:
            payload = _load_json_payload(request)
            updated_fields = _update_instance_from_data(loja, payload, allowed_fields)
        except ValueError as exc:
            return JsonResponse({'detalhe': str(exc)}, status=400)

        response_data = {
            'id': loja.id,
            'updated_fields': updated_fields,
            'loja': {
                'nome': loja.nome,
                'endereco': loja.endereco,
                'telefone': loja.telefone,
                'email': loja.email,
            },
        }
        return JsonResponse(response_data)
    if request.method == 'POST':
        form = LojaForm(request.POST, instance=loja)
        if form.is_valid():
            cleaned_payload = {
                field_name: form.cleaned_data.get(field_name)
                for field_name in form.fields
                if field_name in form.cleaned_data
            }
            try:
                _update_instance_from_data(loja, cleaned_payload, allowed_fields)
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, 'Loja atualizada com sucesso.')
                return redirect('lista_lojas')
    else:
        form = LojaForm(instance=loja)
    return render(request, 'loja_app/loja_form.html', {'form': form})

@staff_member_required
def excluir_loja(request, id):
    loja = get_object_or_404(Loja, id=id)
    # Verifica se existem produtos ou vendas associados
    if Produto.objects.filter(loja=loja).exists() or Venda.objects.filter(loja=loja).exists():
        messages.error(request, f'Não é possível excluir a loja "{loja.nome}", pois ela possui produtos ou vendas associadas.')
        return redirect('lista_lojas')

    if request.method == 'POST':
        loja.delete()
        messages.success(request, f'Loja "{loja.nome}" excluída com sucesso.')
        return redirect('lista_lojas')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': loja, 'tipo': 'Loja'})


# ------------------------------
# CATEGORIAS
# ------------------------------

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
def obter_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    dados = {
        'id': categoria.id,
        'nome': categoria.nome,
    }
    return JsonResponse(dados)

@staff_member_required
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    # Verifica se há produtos usando essa categoria
    if Produto.objects.filter(categoria=categoria).exists():
        messages.error(request, f'Não é possível excluir a categoria "{categoria.nome}", pois ela está em uso por um ou mais produtos.')
        return redirect('lista_categorias')

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, f'Categoria "{categoria.nome}" excluída com sucesso.')
        return redirect('lista_categorias')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': categoria, 'tipo': 'Categoria'})


# ------------------------------
# FORNECEDORES
# ------------------------------

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
    allowed_fields = ['nome', 'cnpj', 'telefone', 'email']

    if request.method in ('PUT', 'PATCH') or _is_json_request(request):
        try:
            payload = _load_json_payload(request)
            updated_fields = _update_instance_from_data(fornecedor, payload, allowed_fields)
        except ValueError as exc:
            return JsonResponse({'detalhe': str(exc)}, status=400)

        return JsonResponse({
            'id': fornecedor.id,
            'updated_fields': updated_fields,
            'fornecedor': {
                'nome': fornecedor.nome,
                'cnpj': fornecedor.cnpj,
                'telefone': fornecedor.telefone,
                'email': fornecedor.email,
            },
        })

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
           cleaned_payload = {
                field_name: form.cleaned_data.get(field_name)
                for field_name in form.fields
                if field_name in form.cleaned_data
            }
        try:
                _update_instance_from_data(fornecedor, cleaned_payload, allowed_fields)
        except ValueError as exc:
                form.add_error(None, str(exc))
        else:
                messages.success(request, 'Fornecedor atualizado com sucesso.')
                return redirect('lista_fornecedores')
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'loja_app/fornecedor_form.html', {'form': form})

@staff_member_required
def obter_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    dados = {
        'id': fornecedor.id,
        'nome': fornecedor.nome,
        'cnpj': fornecedor.cnpj,
        'telefone': fornecedor.telefone,
        'email': fornecedor.email,
    }
    return JsonResponse(dados)

@staff_member_required
def excluir_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    # Verifica se o fornecedor possui produtos
    if Produto.objects.filter(fornecedor=fornecedor).exists():
        messages.error(request, f'Não é possível excluir o fornecedor "{fornecedor.nome}", pois ele está associado a um ou mais produtos.')
        return redirect('lista_fornecedores')

    if request.method == 'POST':
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{fornecedor.nome}" excluído com sucesso.')
        return redirect('lista_fornecedores')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': fornecedor, 'tipo': 'Fornecedor'})


# ------------------------------
# PRODUTOS E ESTOQUE
# ------------------------------

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
    allowed_fields = [
        'nome', 'preco_compra', 'preco_venda', 'categoria', 'fornecedor', 'loja'
    ]

    if request.method in ('PUT', 'PATCH') or _is_json_request(request):
        try:
            payload = _load_json_payload(request)
            updated_fields = _update_instance_from_data(produto, payload, allowed_fields)
        except ValueError as exc:
            return JsonResponse({'detalhe': str(exc)}, status=400)

        return JsonResponse({
            'id': produto.id,
            'updated_fields': updated_fields,
            'produto': {
                'nome': produto.nome,
                'preco_compra': str(produto.preco_compra),
                'preco_venda': str(produto.preco_venda),
                'categoria': produto.categoria.id if produto.categoria else None,
                'fornecedor': produto.fornecedor.id if produto.fornecedor else None,
                'loja': produto.loja.id if produto.loja else None,
            },
        })

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            cleaned_payload = {
                field_name: form.cleaned_data.get(field_name)
                for field_name in form.fields
                if field_name in form.cleaned_data
            }
            try:
                _update_instance_from_data(produto, cleaned_payload, allowed_fields)
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, 'Produto atualizado com sucesso.')
                return redirect('lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'loja_app/produto_form.html', {'form': form})

@staff_member_required
def obter_produto(request, id):
    produto = get_object_or_404(Produto.objects.select_related('categoria', 'fornecedor', 'estoque', 'loja'), id=id)
    dados = {
        'id': produto.id,
        'nome': produto.nome,
        'preco_compra': produto.preco_compra,
        'preco_venda': produto.preco_venda,
        'categoria': {
            'id': produto.categoria.id if produto.categoria else None,
            'nome': produto.categoria.nome if produto.categoria else None,
        },
        'fornecedor': {
            'id': produto.fornecedor.id if produto.fornecedor else None,
            'nome': produto.fornecedor.nome if produto.fornecedor else None,
        },
        'loja': {
            'id': produto.loja.id,
            'nome': produto.loja.nome,
        },
        'estoque': {
            'quantidade': produto.estoque.quantidade if hasattr(produto, 'estoque') else None,
        },
    }
    return JsonResponse(dados)

@staff_member_required
def excluir_produto(request, id):
    produto = get_object_or_404(Produto, id=id)
    # Bloqueia exclusão se tiver histórico
    if ItensVenda.objects.filter(produto=produto).exists() or MovimentacaoEstoque.objects.filter(produto=produto).exists():
        messages.error(request, f'Não é possível excluir o produto "{produto.nome}", pois ele possui histórico de vendas ou movimentações de estoque.')
        return redirect('lista_produtos')

    if request.method == 'POST':
        produto.delete()
        messages.success(request, f'Produto "{produto.nome}" excluído com sucesso.')
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

    context = {'form': form, 'produto': produto, 'estoque': estoque}
    return render(request, 'loja_app/atualizar_estoque.html', context)


# ------------------------------
# CLIENTES
# ------------------------------

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
    allowed_fields = [
        'nome', 'cpf', 'telefone', 'rua', 'numero', 'bairro', 'estado'
    ]

    if request.method in ('PUT', 'PATCH') or _is_json_request(request):
        try:
            payload = _load_json_payload(request)
            updated_fields = _update_instance_from_data(cliente, payload, allowed_fields)
        except ValueError as exc:
            return JsonResponse({'detalhe': str(exc)}, status=400)

        return JsonResponse({
            'id': cliente.id,
            'updated_fields': updated_fields,
            'cliente': {
                'nome': cliente.nome,
                'cpf': cliente.cpf,
                'telefone': cliente.telefone,
                'rua': cliente.rua,
                'numero': cliente.numero,
                'bairro': cliente.bairro,
                'estado': cliente.estado,
            },
        })
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cleaned_payload = {
                field_name: form.cleaned_data.get(field_name)
                for field_name in form.fields
                if field_name in form.cleaned_data
            }
            try:
                _update_instance_from_data(cliente, cleaned_payload, allowed_fields)
            except ValueError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, 'Cliente atualizado com sucesso.')
                return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'loja_app/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente'})

@staff_member_required
def obter_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    dados = {
        'id': cliente.id,
        'nome': cliente.nome,
        'cpf': cliente.cpf,
        'telefone': cliente.telefone,
        'rua': cliente.rua,
        'numero': cliente.numero,
        'bairro': cliente.bairro,
        'estado': cliente.estado,
    }
    return JsonResponse(dados)

@staff_member_required
def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    # Bloqueia exclusão se tiver vendas
    if Venda.objects.filter(cliente=cliente).exists():
        messages.error(request, f'Não é possível excluir o cliente "{cliente.nome}", pois ele possui vendas registradas.')
        return redirect('lista_clientes')

    if request.method == 'POST':
        cliente.delete()
        messages.success(request, f'Cliente "{cliente.nome}" excluído com sucesso.')
        return redirect('lista_clientes')
    return render(request, 'loja_app/confirm_delete.html', {'objeto': cliente, 'tipo': 'Cliente'})


# ------------------------------
# VENDAS
# ------------------------------

@staff_member_required
def lista_vendas(request):
    vendas = Venda.objects.all().order_by('-data_venda')
    return render(request, 'loja_app/venda_list.html', {'vendas': vendas})

@staff_member_required
@transaction.atomic 
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

                    if produto.estoque.quantidade < quantidade:
                        messages.error(request, f"Estoque insuficiente para o produto: {produto.nome}. Disponível: {produto.estoque.quantidade}")
                        return redirect('registrar_venda')

                    item = form.save(commit=False)
                    item.venda = venda
                    item.preco_unitario = produto.preco_venda
                    item.save()

                    estoque = produto.estoque
                    estoque.quantidade -= quantidade
                    estoque.save()

                    MovimentacaoEstoque.objects.create(
                        produto=produto,
                        quantidade=quantidade,
                        tipo='SAIDA',
                        descricao=f"Venda #{venda.id}"
                    )

                    valor_total_venda += item.preco_unitario * item.quantidade

            venda.valor_total = valor_total_venda
            venda.save()
            return redirect('lista_vendas')
    else:
        venda_form = VendaForm()
        item_formset = ItemVendaFormSet()

    context = {'venda_form': venda_form, 'item_formset': item_formset, 'titulo': 'Registrar Nova Venda'}
    return render(request, 'loja_app/venda_form.html', context)


@staff_member_required
@transaction.atomic
def cancelar_venda(request, venda_id):
    venda = get_object_or_404(Venda, id=venda_id)
    if venda.status == 'CANCELADA':
        messages.error(request, 'Esta venda já foi cancelada.')
        return redirect('lista_vendas')

    if request.method == 'POST':
       venda_identificador = venda.id
       itens_venda = list(venda.itens.select_related('produto', 'produto__estoque'))

       for item in itens_venda:
            estoque = item.produto.estoque
            estoque.quantidade += item.quantidade
            estoque.save()
            MovimentacaoEstoque.objects.create(
                produto=item.produto,
                quantidade=item.quantidade,
                tipo='ENTRADA',
                descricao=f'Estorno por cancelamento da Venda #{venda_identificador}'
            )
    
    venda.itens.all().delete()
    venda.delete()
    messages.success(
            request,
            f'Venda #{venda_identificador} cancelada e removida com sucesso. O estoque foi atualizado.'
        )
    return redirect('lista_vendas')

    return render(request, 'loja_app/confirm_cancel.html', {'venda': venda})


# ------------------------------
# RELATÓRIOS / APIs
# ------------------------------

@staff_member_required
def relatorio_vendas_cliente(request, cliente_id):
    """Retorna as vendas de um cliente agregando itens no formato "Produto (xQuantidade)"."""
    cliente = get_object_or_404(Cliente, id=cliente_id)

    vendas_queryset = (
        Venda.objects.filter(cliente_id=cliente_id)
        .select_related('loja')
        .prefetch_related(
            Prefetch(
                'itens',
                queryset=ItensVenda.objects.select_related('produto').order_by('produto__nome', 'id'),
            )
        )
        .order_by('-data_venda')
    )

    vendas_formatadas = []
    for venda in vendas_queryset:
        itens_descricao = [
            f"{item.produto.nome} (x{item.quantidade})"
            for item in venda.itens.all()
        ]

        vendas_formatadas.append({
            'id': venda.id,
            'loja': venda.loja.nome if venda.loja else None,
            'data_venda': venda.data_venda.isoformat(),
            'valor_total': str(venda.valor_total),
            'status': venda.get_status_display(),
            'itens_descricao': ', '.join(itens_descricao),
        })

    resposta = {
        'cliente': {
            'id': cliente.id,
            'nome': cliente.nome,
        },
        'vendas': vendas_formatadas,
    }

    return JsonResponse(resposta)




# ------------------------------
# AJAX
# ------------------------------

def get_produtos_por_loja(request):
    loja_id = request.GET.get('loja_id')
    produtos = Produto.objects.filter(loja_id=loja_id).order_by('nome')
    return JsonResponse(list(produtos.values('id', 'nome')), safe=False)

@staff_member_required
def lista_itens_venda(request):
    itens_venda = ItensVenda.objects.all().order_by('-venda__data_venda')
    return render(request, 'loja_app/itens_venda_list.html', {'itens_venda': itens_venda})

@staff_member_required
def lista_movimentacoes_estoque(request):
    movimentacoes = MovimentacaoEstoque.objects.all().order_by('-data')
    return render(request, 'loja_app/movimentacao_estoque_list.html', {'movimentacoes': movimentacoes})

# ------------------------------
# HISTÓRICO DE COMPRAS (CLIENTE)
# ------------------------------
@login_required
def meu_historico_compras(request):
    vendas_cliente = []
    cliente_profile = None
    
    # Apenas usuários não-staff (clientes) devem ter um histórico de compras pessoal
    if not request.user.is_staff:
        try:
            # Tenta encontrar o perfil de cliente vinculado a este usuário
            cliente_profile = Cliente.objects.get(user=request.user)
            # Filtra as vendas apenas para este cliente
            vendas_cliente = Venda.objects.filter(cliente=cliente_profile).order_by('-data_venda')
        except Cliente.DoesNotExist:
            # O usuário logado não tem um perfil de cliente
            # (Talvez um usuário antigo antes da mudança ou um erro)
            messages.error(request, 'Não foi possível encontrar seu perfil de cliente.')
            pass 

    context = {
        'vendas': vendas_cliente,
        'cliente_profile': cliente_profile
    }
    return render(request, 'loja_app/meu_historico_compras.html', context)