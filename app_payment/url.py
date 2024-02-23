from django.urls import path
from .views import *

urlpatterns = [
    path('', imprimir, name='notification'), # type: ignore
    path('/pix', imprimirPix, name='imprimirPix'), # type: ignore
    path('/pay', page_payments, name='payment'), 
    path('/pay_pix', criar_pagamento_pix, name='pay_pix'), # type: ignore
    path('/pay_cartao', criar_pagamento_cartao, name="pay_cartao"), # type: ignore
    path("/conclusao_pagamento_cartao", conclusao_pagamento_cartao, name="conclusao_pagamento_cartao"), # type: ignore
    path('/conf_conta', enviar_conf_conta, name="conf_conta"),
    path('/flag', flagscard, name='flag'), # type: ignore
    path('/listando', listando, name='listando'),
    path('/notificacaopagamentos', notificacaoCobrancas, name="notificacaopagamentos"),
    path('/pagamentoconcluido/<str:txid_payment_token>', pagamento_concluido, name='pagamentoconcluido'),
]