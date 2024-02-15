from django.urls import path
from .views import *

urlpatterns = [
    path('', imprimir, name='notification'),
    path('/pix', imprimirPix, name='imprimirPix'),
    path('/pay', page_payments, name='payment'),
    path('/pay_pix', criar_pagamento_pix, name='pay_pix'),
    path('/pay_cartao', criar_pagamento_cartao, name="pay_cartao"),
    path("/conclusao_pagamento_cartao", conclusao_pagamento_cartao, name="conclusao_pagamento_cartao"),
    path('/conf_conta', enviar_conf_conta, name="conf_conta"),
    path('/flag', flagscard, name='flag'),
    path('/listando', listando, name='listando'),
    path('/notificacaopagamentos', notificacaoCobrancas, name="notificacaopagamentos"),
    path('/pagamentoconcluido/<int:charge_id>', pagamento_concluido, name='pagamentoconcluido'),
]