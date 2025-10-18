from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 🏠 Página inicial (home pública)
    path('', views.home, name='home'),

    # 🔐 Login e Logout
    path('login/', auth_views.LoginView.as_view(template_name='loja_app/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 👤 Registro de usuário
    path('registrar/', views.registrar_view, name='registrar'),

    # 📊 Dashboard (página protegida)
    path('dashboard/', views.home, name='dashboard'),

    # ℹ️ Sobre nós
    path('sobre-nos/', views.about_us_view, name='about_us'),

    # 🏬 Lojas (somente para admin)
    path('lojas/', views.lista_lojas, name='lista_lojas'),
    path('lojas/cadastrar/', views.cadastrar_loja, name='cadastrar_loja'),
    path('lojas/editar/<int:id>/', views.editar_loja, name='editar_loja'),
    path('lojas/excluir/<int:id>/', views.excluir_loja, name='excluir_loja'),
]
