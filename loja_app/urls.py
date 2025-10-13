from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # A ROTA PRINCIPAL AGORA É O LOGIN
    path('', auth_views.LoginView.as_view(template_name='loja_app/login.html'), name='login'),
    path('dashboard/', views.home, name='dashboard'),

     # NOVA ROTA PARA A PÁGINA "SOBRE NÓS"
    path('sobre-nos/', views.about_us_view, name='about_us'),

    # ROTA PARA A NOVA PÁGINA DE REGISTRO DE CONTA
    path('registrar/', views.registrar_view, name='registrar'),

    # A ANTIGA PÁGINA 'HOME' AGORA É O 'DASHBOARD'
    path('dashboard/', views.home, name='dashboard'),

    # URLS EXISTENTES DE GERENCIAMENTO DE LOJAS
    path('lojas/', views.lista_lojas, name='lista_lojas'),
    path('lojas/cadastrar/', views.cadastrar_loja, name='cadastrar_loja'),
    path('lojas/editar/<int:id>/', views.editar_loja, name='editar_loja'),
    path('lojas/excluir/<int:id>/', views.excluir_loja, name='excluir_loja'),
    
    # ROTA DE LOGOUT
    path('logout/', views.logout_view, name='logout'),
]