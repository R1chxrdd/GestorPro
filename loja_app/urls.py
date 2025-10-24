from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='loja_app/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.registrar_view, name='registrar'),
    path('dashboard/', views.home, name='dashboard'),
    path('sobre-nos/', views.about_us_view, name='about_us'),

    path('lojas/', views.lista_lojas, name='lista_lojas'),
    path('lojas/cadastrar/', views.cadastrar_loja, name='cadastrar_loja'),
    path('lojas/editar/<int:id>/', views.editar_loja, name='editar_loja'),
    path('lojas/excluir/<int:id>/', views.excluir_loja, name='excluir_loja'),


    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/cadastrar/', views.cadastrar_categoria, name='cadastrar_categoria'),
    path('categorias/excluir/<int:id>/', views.excluir_categoria, name='excluir_categoria'),

    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/cadastrar/', views.cadastrar_fornecedor, name='cadastrar_fornecedor'),
    path('fornecedores/editar/<int:id>/', views.editar_fornecedor, name='editar_fornecedor'),
    path('fornecedores/excluir/<int:id>/', views.excluir_fornecedor, name='excluir_fornecedor'),
    
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/cadastrar/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produtos/editar/<int:id>/', views.editar_produto, name='editar_produto'),
    path('produtos/excluir/<int:id>/', views.excluir_produto, name='excluir_produto'),
    path('produtos/<int:produto_id>/atualizar_estoque/', views.atualizar_estoque, name='atualizar_estoque'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:id>/', views.excluir_cliente, name='excluir_cliente'),
    path('vendas/', views.lista_vendas, name='lista_vendas'),
    path('vendas/registrar/', views.registrar_venda, name='registrar_venda'),
    path('vendas/cancelar/<int:venda_id>/', views.cancelar_venda, name='cancelar_venda'),
    path('api/get-produtos-por-loja/', views.get_produtos_por_loja, name='get_produtos_por_loja'),
    path('historico/itens-vendidos/', views.lista_itens_venda, name='lista_itens_venda'),
    path('historico/movimentacoes-estoque/', views.lista_movimentacoes_estoque, name='lista_movimentacoes_estoque'),
]