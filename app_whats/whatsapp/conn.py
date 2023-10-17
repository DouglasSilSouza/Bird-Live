from .models_whatsapp import modelos_whatsapp
from dotenv import load_dotenv
import traceback
import tempfile
import requests
import base64
import json
import uuid
import re
import os

# Load the stored environment variables
load_dotenv()

class Conn_Whatsapp:
    def __init__(self) -> None:
        self.url = os.getenv("URL")
        self.phone_number_id = '103394759172111'
        self.token = os.getenv("TOKEN")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
        }
        self.session = requests.session()

    def enviar_mensagem(self, to, body):
        url_formated = f"{self.url}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "text",
            "to": to,
            "text": {"body": body},
        }
        
        response = requests.post(url_formated, json=payload, headers=self.headers)
        return response
    
    def enviar_modelo(self, to, model, nome=None):

        url_formated = f"{self.url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "type": "template",
            "to": to,
            "template": modelos_whatsapp(model, nome)
        }

        response = requests.post(url_formated, json=payload, headers=self.headers)
        return response
    
    def image_get(self, id_image):
        url_formated = f'{self.url}/{id_image}'
        payload = {
            'phone_number_id': self.phone_number_id
        }

        response = requests.get(url_formated, json=payload, headers=self.headers)

        if response.status_code == 200:
            try:
                url_image = response.json().get('url')
                mime_type = response.json().get('mime_type')
                tamanho_imagem = response.json().get('file_size')
                file_id_whatsapp = response.json().get('id')

                try:
                    get_image = requests.get(url=url_image, headers=self.headers)
                    if get_image.status_code == 200:
                        # Codifique os bytes em formato base64
                        base64_data = base64.b64encode(get_image.content).decode('utf-8')
                        return {'mime_type':mime_type, 'file_size':tamanho_imagem, 'file_id_whatsapp':file_id_whatsapp, 'file_message':base64_data}   
                    else:
                        print(f'Erro| Código de Status: {get_image.status_code}')
                        return None
                except requests.exceptions.RequestException as e:
                    print("Erro ao baixar a imagem:", e)
                    return None
            except requests.exceptions.RequestException as e:
                print(f'Erro na solicitação HTTP: {e}')
                return None
        else:
            print(f"Erro ao pegar a imagem| Código de Status: {response.status_code}")
            return None

    def send_image(self, numero, image_data):
        url_formated = f'{self.url}/{self.phone_number_id}/media'

        # Extrair o formato da imagem da string base64
        format_match = re.search(r"data:image/(\w+);base64,", image_data)
        image_format = format_match.group(1)

        # Remover o prefixo da string base64
        base64_data = re.sub(r"data:image/(\w+);base64,", "", image_data)

        # Decodificar a string base64 para bytes
        image_data = base64.b64decode(base64_data)

        # Gerar um nome de arquivo aleatório com base no formato da imagem
        file_name = "{}.{}".format(uuid.uuid4().hex, image_format)

        # Criar um arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(suffix="." + image_format, delete=False)
        temp_file.write(image_data)
        temp_file.close()

        # Obter o caminho absoluto do arquivo temporário
        file_path = temp_file.name
        file_path = file_path.replace("\\", "/")

        payload = {
            "messaging_product": "whatsapp",
            "type": "image",
            }

        files = [
            ('file',(file_name, open(file_path, "rb"), 'image/{}'.format(image_format)))
        ]

        header = {"Authorization": self.token,}

        response = self.session.post(url_formated, headers=header, data=payload, files=files)
        if response.status_code == 200:
            response_json = response.json()
            url_send_image = f"{self.url}/{self.phone_number_id}/messages"
            payload_image = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "type": "image",
                "to": numero,
                "image": {
                    "id" : response_json.get('id')
                }
            }
            send_image = requests.post(url_send_image, json=payload_image, headers=self.headers)
            if send_image.status_code == 200:
                return send_image, response_json
            else:
                print(f"Erro ao enviar a Image: {send_image.text}")
                return send_image
        else:
            print(f"Erro ao pegar a ID da Imagem: {response.text}")
            return response
                