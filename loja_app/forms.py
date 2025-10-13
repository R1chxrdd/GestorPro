from django import forms
from .models import Loja
from django.contrib.auth.forms import UserCreationForm

class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = ['nome', 'endereco', 'telefone', 'email']

# formulário de registro de usuário
class UserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'email'] # adiciona mais campos se quiser