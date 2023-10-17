from channels.generic.websocket import AsyncWebsocketConsumer
import base64
import json

class ReceberMensagemConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.numerotelefone = self.scope['url_route']['kwargs']['numero_telefone']  # Obtenha o número de telefone da URL
        self.conversa_id = "conversa_%s" % self.numerotelefone

        # Adicionar o cliente ao grupo WebSocket
        await self.channel_layer.group_add(
            self.conversa_id,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remover o cliente do grupo WebSocket
        await self.channel_layer.group_discard(
            self.conversa_id,
            self.channel_name
        )
    
    async def receive(self, text_data):
        # Decodifique o JSON recebido
        data = json.loads(text_data)
        # Enviar a mensagem recebida para todos os participantes da sala
        await self.channel_layer.group_send(
            self.conversa_id,
            {
                'type': 'chat_message',
                'type_conteudo': data['type_conteudo'],
                'message': data['message'],
                'numerotelefone' : data['numerotelefone'],
                'hora_back': data['hora_back'],
            }
        )

    async def chat_message(self, event):
        message = event['message']
        numerotelefone = event['numerotelefone']
        hora_back = event['hora_back']
        type_conteudo = event['type_conteudo']

        # Enviar mensagem para o cliente JavaScript
        await self.send(text_data=json.dumps({
            'type_conteudo': type_conteudo,
            'message': message,
            'numerotelefone' : numerotelefone,
            'hora_back': hora_back,
        }))
    
    async def chat_image(self, event):
        # Decodifica a imagem a partir da base64
        image_data = event['image']
        numerotelefone = event['numerotelefone']
        hora_back = event['hora_back']
        type_conteudo = event['type_conteudo']
        type_arq = event['type_arq']

        # Enviar mensagem para o cliente JavaScript
        await self.send(text_data=json.dumps({
            'type_conteudo': type_conteudo,
            'image_data': image_data,
            'numerotelefone' : numerotelefone,
            'hora_back': hora_back,
            'type_arq': type_arq,
        }))

    async def statuses(self, status_event):
        status = status_event['status']
        wa_id_message = status_event['wa_id_message']
        type_conteudo = status_event['type_conteudo']
        error = status_event['error']

        # Enviar mensagem para o cliente JavaScript
        await self.send(text_data=json.dumps({
            'type_conteudo': type_conteudo,
            'status': status,
            'wa_id_message': wa_id_message,
            'error': error,
        }))

        