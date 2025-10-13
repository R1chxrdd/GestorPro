from django.db import models

class Loja(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Loja")
    endereco = models.CharField(max_length=200, verbose_name="Endereço")
    telefone = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)

    def __str__(self):
        return self.nome

