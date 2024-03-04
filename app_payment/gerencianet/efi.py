from ecommerce_cart.models import Carrinho, ItemCarrinho
from channels.db import database_sync_to_async
from efipay import EfiPay
from .get_endereco import endereco
from datetime import datetime
from decimal import Decimal
import traceback
import re
from os import getenv
import dotenv

dotenv.load_dotenv()

sandbox = {
            'client_id': getenv('CLIENT_ID'),
            'client_secret': getenv('CLIENT_SECET'),
            'sandbox': True,
            'certificate': r".\homologacao-547180-teste_cert.pem"
        }

efi = EfiPay(sandbox)

class Pagamento:
    def __init__(self, CartID=None):
        self.CartID = CartID
        self.cart = None
        self.items = None
        self.user = None

    @database_sync_to_async
    def get_cart(self):
        return Carrinho.objects.get(pk=self.CartID)
    
    @database_sync_to_async
    def get_user(self):
        return self.cart.usuario
    
    @database_sync_to_async
    def get_items(self):
        return ItemCarrinho.objects.filter(carrinho=self.cart)

    async def initialize(self):
        self.cart = await self.get_cart()
        self.items = await self.get_items()
        self.user = await self.get_user()

    @database_sync_to_async
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

    @database_sync_to_async
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

    @database_sync_to_async
    def complete_payment_card(self, parcela, token, id, erropayment):
        user = self.user
        pegar_endereco = endereco(user.cep)

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
            if erropayment == 'true':
                response = efi.retry_payment(params=params,body=body)
            else:
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