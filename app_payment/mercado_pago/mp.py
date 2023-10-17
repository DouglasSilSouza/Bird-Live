from ecommerce_main.products.getproducts import GetProducts
import requests
import json
import os

class MercadoPago:
    def __init__(self, usuario) -> None:
        self.token = os.getenv("MP_TOKEN")
        self.url_base = "https://api.mercadopago.com"
        self.session = requests.Session()
        self.user = usuario
        
    
    def criar_pagamento(self, data):
        url = self.url_base + "/v1/payments"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}

        dados = data.get("description")
        # Inicializando a string de descrição
        descricao_itens = "Descrição dos itens: "

        # Percorrendo os itens e adicionando à string
        for item in dados:
            descricao_itens += f"ID: {item['product_id']} e Quantidade: {item['quantity']} e Titulo: {item['title']} e Subtotal: {item['subtotal']},"

        user = self.user
        params = json.dumps({
                    "transaction_amount": data.get("transaction_amount"),
                    "installments": data.get("installments"),
                    "description": descricao_itens,
                    "payment_method_id": data.get("payment_method_id"),
                    "payer": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "identification": {
                            "type": user.type_document,
                            "number": user.cpf_cnpj,
                        },
                        "address": {
                            "zip_code": user.cep,
                            "street_name": user.endereco,
                            "street_number": user.number,
                            "neighborhood": user.bairro,
                        }
                    },
                    "token": data.get("token"),
                })
        
        response = self.session.post(url, headers=headers, data=params)

        return response