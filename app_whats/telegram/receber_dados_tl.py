from app_whats.models import Destinatario, Conversa, Mensagem, Files_WhatsApp_Message
from django.core.exceptions import ObjectDoesNotExist
from channels.layers import get_channel_layer
from django.db.utils import IntegrityError
from asgiref.sync import async_to_sync
from datetime import datetime
import traceback
import json

class ReceberDados_tl:
    def __init__(self, payload) -> None:
        self.payload = payload
    
    def receber_mensagem(self):
        try:
            id = self.payload.get('from').get('id') #ID do cliente no Telegram
            nome = self.payload.get('from').get('first_name')
            sobrenome = self.payload.get('from').get('last_name')
            timestamp =datetime.fromtimestamp(int(self.payload.get('date'))) 
            formated_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            msg = self.payload.get('text')
            id_mensagem = self.payload.get('message_id') # ID da mensagem recebida

            try:
                destinatario = Destinatario.objects.get(nome_destinatario = f'{nome} {sobrenome}')

                try:
                    conversa = Conversa.objects.get(identificador_conversa=f"conversa_{id}", status_room='novo', canal='telegram')
                    # Se a conversa existe, verifique o status
                    if conversa.status_room == 'novo':
                        # Salvar a mensagem no banco de dados
                        Mensagem.objects.create(
                            conversa=conversa,
                            conteudo=msg,
                            tipo='recebida',
                            data_hora_message=formated_timestamp,
                            wa_id_message= id_mensagem,
                        )
                except Conversa.DoesNotExist:
                    # Se a conversa não existir, crie um novo registro
                    conversa = Conversa(identificador_conversa=f"conversa_{id}", usuario=self.payload.get('from').get('username'), destinatario=destinatario, status_room='novo', canal='telegram')
                    conversa.save()
            
                # Enviar mensagem para o WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'conversa_{id}',  # Nome do grupo WebSocket
                    {
                        'type': 'chat_message',
                        'type_conteudo': 'text',
                        'message': msg,
                        'numerotelefone' : destinatario.numero_telefone_telegram,
                        'hora_back': timestamp.strftime("%H:%M"),
                    }
                )
            except Exception as e:
                print(e)
                traceback_str = traceback.format_exc()
                print(f"Erro: {traceback_str}")
                data = ''
            return data
        except Destinatario.DoesNotExist as e:
                print(e)
                traceback_str = traceback.format_exc()
                print(f"Erro: {traceback_str}")
                data = "usuario não encontrado!"
        return data 