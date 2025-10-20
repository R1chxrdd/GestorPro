from django import forms
from .models import Loja, Categoria, Fornecedor
from django.contrib.auth.forms import UserCreationForm

class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = ['nome', 'endereco', 'telefone', 'email']

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