from django import forms
from .models import Loja, Categoria, Fornecedor, Produto 
from django.contrib.auth.forms import UserCreationForm
from .models import Loja, Categoria, Fornecedor, Produto, Cliente 
from .models import Loja, Categoria, Fornecedor, Produto, Cliente, Venda, ItensVenda 

class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = ['nome', 'endereco', 'telefone', 'email', 'cnpj_loja']

class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'email']

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'cnpj', 'telefone', 'email']

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'preco_compra', 'preco_venda', 'categoria', 'fornecedor', 'loja']

class MovimentacaoEstoqueForm(forms.Form):
    quantidade = forms.IntegerField(label="Quantidade para Movimentar")
    descricao = forms.CharField(label="Descrição (Opcional)", required=False, widget=forms.Textarea(attrs={'rows': 3}))

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'telefone', 'rua', 'numero', 'bairro', 'estado']

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente', 'loja']

class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItensVenda
        fields = ['produto', 'quantidade']