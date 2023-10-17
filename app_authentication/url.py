from django.urls import path
from .views import *

urlpatterns = [
    path('login', login_view, name='login_view'),
    path('login_colab', login_view_colab, name='login_colab'),
    path('cadastro_collaborator', cadastro_colaborador, name='cadastro_collaborator'),
    path('cadastro_user', cadastro_usuario, name='cadastro_user'),
    path('logout', logout_view, name='logout_view'),
    path('configuracoes/', configuracoes, name='configuracoes'),
]