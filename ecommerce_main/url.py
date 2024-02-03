from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='e-home'),
    path('<int:id>/', productOnly, name='productonly'),
    path('countcart', base, name='countcart'),
    path('dados_pessoais/', dados_pessoais, name='dados_pessoais'),
    path('change_password/', change_password, name='change_password'),
    path('historico/', historico_compras, name='historico'),
    path('historico/<int:id_payment>/', prod_historico_compra, name='prod_historico_compra'),
]