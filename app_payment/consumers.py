# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            # Adiciona o usuário ao grupo específico
            group_name = f"user_{user.id}"
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )

            # Aceita a conexão
            await self.accept()
        else:
            print("Usuário não autenticado tentou se conectar. Conexão recusada.")
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            (f"{user.first_name} Autenticado e Desconectado")
            # Remove o usuário do grupo específico
            await self.channel_layer.group_discard(
                f"user_{user.id}",
                self.channel_name
            )

    async def receive(self, text_data):
        # Processar dados recebidos, se necessário
        pass

    async def send_notification(self, event):
        status = event['status']
        txid_status = event['txid_status']

        # Envia a mensagem para o frontend
        await self.send(text_data=json.dumps({
            'status': status,
            'txid_status': txid_status
        }))
