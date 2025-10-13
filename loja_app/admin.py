from django.contrib import admin
from .models import Loja

@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'endereco', 'telefone', 'email')
    search_fields = ('nome', 'endereco')

