from efipay import EfiPay
from .variaveis import GetSecret
from ecommerce_cart.models import Carrinho, ItemCarrinho
from .get_endereco import endereco
from datetime import datetime
from decimal import Decimal
import traceback
import re

variavel = GetSecret.get_secret()

credentials = {
    'client_id': variavel['CLIENT_ID'],
    'client_secret': variavel['CLIENT_SECRET'],
    'sandbox': True,
    'certificate': r"C:\Users\dougl\OneDrive\Área de Trabalho\programação\requisitos efi\conversor-p12-efi-main\conversor-p12-efi-main\homologacao-547180-teste_cert.pem"
}

# credentials = {
#     'client_id': 'Client_Id_80f7735a77a3dae4bbbe11a5b8aa3ee7617608db',
#     'client_secret': 'Client_Secret_341537cf57c5769897203e3a0628b810ee2c02b2',
#     'sandbox': False,
#     'certificate': r"C:\Users\dougl\OneDrive\Área de Trabalho\programação\requisitos efi\conversor-p12-efi-main\conversor-p12-efi-main\producao-547180-Bird-Live_cert.pem"
# }


efi = EfiPay(credentials)

class Pagamento:
    def __init__(self, CartID = None) -> None:
        self.CartID = CartID
        if self.CartID:
            self.cart = Carrinho.objects.get(pk=self.CartID)
            self.items = ItemCarrinho.objects.filter(carrinho=self.cart)
            self.user = self.cart.usuario
        else:
            self.cart = None
            self.items = None
            self.user = None

    def creat_pay_pix(self):
        user = self.user
        body = {
            'calendario': {
                'expiracao': 3600
            },
            'devedor': {
                "nome": f"{user.first_name} {user.last_name}",
                "cpf": (user.cpf_cnpj).replace(".", "").replace("-",""),
            },
            'valor': {
                'original': '0.01'
            },
            'chave': 'a1541545-0bf2-4826-8435-17988605f3b7',
            'solicitacaoPagador': 'Teste em Produção.'
        }

        response =  efi.pix_create_immediate_charge(body=body)
        return response
    
    def creat_qrcode_pix(self,id):
        params = {
            "id": id
        }
        response = efi.pix_generate_qrcode(params=params)
        return response

    def pix_detail(self, txid):
        params = {
            "txid": txid
        }
        response = efi.pix_detail_charge(params=params)
        return response

    def creat_pay_cartao(self):
        items = self.items.values_list('title', 'quantidade', 'valor_unitario')
        itens = []
        for i in items:
            itens.append({
                "name": i[0],
                "value": int(float(i[2].quantize(Decimal('1.00'))) * 100),
                "amount": i[1],
            })

        user = self.user

        body = {
            "items": itens,
            "metadata": {
                "custom_id": (user.cpf_cnpj).replace(".", "").replace("-",""),
                "notification_url": "https://bird-live-ewe.ngrok-free.app/payments/notificacaopagamentos"
            }
        }

        response = efi.create_charge(body=body)
        return response        

    def complete_payment_card(self, parcela, token, id):
        pegar_endereco = endereco(self.user.cep)
        user = self.user

        padrao_phone = re.compile(r'^[1-9]{2}9?[0-9]{8}$')
        usuario = (user.phone).replace(" ","")
        phone = padrao_phone.findall(usuario)[0]

        try:
            params = {
                "id": id
            }

            body = {
                "payment": {
                    "credit_card": {
                        "customer": {
                            "name": f"{user.first_name} {user.last_name}",
                            "cpf": (user.cpf_cnpj).replace(".", "").replace("-",""),
                            "email": user.email,
                            "birth": datetime.strftime(user.date_birthday, "%Y-%m-%d"),
                            "phone_number": phone
                        },
                        "installments": int(parcela),
                        "payment_token": token,
                        "billing_address": {
                            "street": user.endereco,
                            "number": user.number,
                            "neighborhood": user.bairro,
                            "zipcode": user.cep,
                            "city": pegar_endereco['city'],
                            "complement": "",
                            "state": pegar_endereco['state']
                        }
                    }
                }
            }
            response = efi.define_pay_method(params=params,body=body)
        except Exception as e:
            response = str(e)
            traceback.print_exc()
        return response

    def get_notification_cobranca(self, token_notification):
        params = {
            "token": token_notification
        }
        response = efi.get_notification(params=params)
        return response

    def list_webhook(self):
        params = {
            "inicio": "2024-02-01T00:00:00Z",
            "fim": "2024-02-28T00:00:00Z"
        }
        response = efi.pix_list_webhook(params=params)
        return response
    
    def set_webhook(self):
        params = {
            "chave": 'a1541545-0bf2-4826-8435-17988605f3b7'
        }

        headers = {
            "x-skip-mtls-checking": "true"
        }

        body = {
            "webhookUrl": "https://bird-live-ewe.ngrok-free.app/payments"
        }
    
        response = efi.pix_config_webhook(params=params, headers=headers, body=body)
        return response