from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Loja(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Loja")
    endereco = models.CharField(max_length=200, verbose_name="Endereço")
    telefone = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)

    def __str__(self):
        return self.nome

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")

    def __str__(self):
        return self.nome

class Fornecedor(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Fornecedor")
    cnpj = models.CharField(max_length=20, verbose_name="CNPJ", unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)

    def __str__(self):
        return self.nome

class Cliente(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Cliente")
    cpf = models.CharField(max_length=14, verbose_name="CPF", unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=15, verbose_name="Telefone", blank=True, null=True)
    rua = models.CharField(max_length=200, verbose_name="Rua", blank=True, null=True)
    numero = models.CharField(max_length=10, verbose_name="Número", blank=True, null=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", blank=True, null=True)
    estado = models.CharField(max_length=50, verbose_name="Estado", blank=True, null=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    preco_compra = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Compra")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

class Estoque(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=0)

    def __str__(self):
        return f"Estoque de {self.produto.nome}"

@receiver(post_save, sender=Produto)
def criar_estoque_para_produto(sender, instance, created, **kwargs):
    if created:
        Estoque.objects.create(produto=instance)


class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTACAO = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=7, choices=TIPO_MOVIMENTACAO)
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} de {self.quantidade} em {self.produto.nome}"

class Venda(models.Model):
    STATUS_CHOICES = [
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    data_venda = models.DateTimeField(default=timezone.now)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONCLUIDA') # <-- CAMPO ADICIONADO

    def __str__(self):
        return f"Venda #{self.id} - Status: {self.get_status_display()}"

class ItensVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"