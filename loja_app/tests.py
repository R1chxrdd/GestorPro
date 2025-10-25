from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Cliente, Loja, Produto, Venda, ItensVenda


class RelatorioVendasClienteViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='staff', password='senha123', is_staff=True
        )

        self.cliente = Cliente.objects.create(nome='Cliente Teste')
        self.loja = Loja.objects.create(nome='Loja Teste', endereco='Rua A', telefone='123')

        self.produto_a = Produto.objects.create(
            nome='Produto A',
            preco_compra=10,
            preco_venda=20,
            loja=self.loja,
        )
        self.produto_b = Produto.objects.create(
            nome='Produto B',
            preco_compra=15,
            preco_venda=30,
            loja=self.loja,
        )

        self.venda = Venda.objects.create(cliente=self.cliente, loja=self.loja, valor_total=50)
        ItensVenda.objects.create(venda=self.venda, produto=self.produto_a, quantidade=2, preco_unitario=20)
        ItensVenda.objects.create(venda=self.venda, produto=self.produto_b, quantidade=1, preco_unitario=30)

    def test_relatorio_retorna_itens_agrupados(self):
        self.client.login(username='staff', password='senha123')

        url = reverse('relatorio_vendas_cliente', args=[self.cliente.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload['cliente']['id'], self.cliente.id)
        self.assertEqual(len(payload['vendas']), 1)
        self.assertEqual(
            payload['vendas'][0]['itens_descricao'],
            'Produto A (x2), Produto B (x1)'
        )

