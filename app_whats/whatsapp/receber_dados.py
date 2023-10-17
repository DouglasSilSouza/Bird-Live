from app_whats.models import Destinatario, Conversa, Mensagem, Files_WhatsApp_Message
from django.core.exceptions import ObjectDoesNotExist
from app_whats.whatsapp.conn import Conn_Whatsapp
from channels.layers import get_channel_layer
from django.db.utils import IntegrityError
from asgiref.sync import async_to_sync
from datetime import datetime
import traceback
import json

class Receber_dados:
    def __init__(self, payload) -> None:
        self.payload = payload

    def receber_mensagem(self):
        try:
            numero_destinatario = self.payload.get('messages')[0].get('from') # Telefone da conversa
            wa_id = self.payload.get('contacts')[0].get('wa_id') #ID do cliente no Whatsapp (Número de Telefone)
            name = self.payload.get('contacts')[0].get('profile').get('name')
            timestamp =datetime.fromtimestamp(int(self.payload.get('messages')[0].get('timestamp'))) 
            formated_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            msg = self.payload.get('messages')[0].get('text').get('body')
            id_mensagem = self.payload.get('messages')[0].get('id') # ID da mensagem recebida

            data = {'mensagem': msg, 'nome': name, 'numero': wa_id}

            # Verificar se o destinatário já existe
            # Atualizar ou criar o destinatário
            destinatario, _ = Destinatario.objects.update_or_create(
                    numero_telefone=numero_destinatario,
                    defaults={
                        'whatsapp_id': wa_id,
                        'nome_destinatario': name,
                    }
            )

            try:
                conversa = Conversa.objects.get(identificador_conversa=f"conversa_{wa_id}", status_room='novo', canal='whatsapp')
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
                conversa = Conversa(identificador_conversa=f"conversa_{wa_id}", usuario=None, destinatario=destinatario, status_room='novo', canal='whatsapp')
                conversa.save()
          
            # Enviar mensagem para o WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'conversa_{wa_id}',  # Nome do grupo WebSocket
                {
                    'type': 'chat_message',
                    'type_conteudo': 'text',
                    'message': msg,
                    'numerotelefone' : numero_destinatario,
                    'hora_back': timestamp.strftime("%H:%M"),
                }
            )
        except Exception as e:
            print(e)
            traceback_str = traceback.format_exc()
            print(f"Erro: {traceback_str}")
        return data 

    def receveid_file(self):
        try:
            numero_destinatario = self.payload.get('messages')[0].get('from') # Telefone da conversa
            wa_id = self.payload.get('contacts')[0].get('wa_id') #ID do cliente no Whatsapp (Número de Telefone)
            name = self.payload.get('contacts')[0].get('profile').get('name')
            timestamp =datetime.fromtimestamp(int(self.payload.get('messages')[0].get('timestamp'))) 
            formated_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            image = self.payload.get('messages')[0].get('image')
            caption = image.get('caption')
            id_image = image.get('id')
            id_mensagem = self.payload.get('messages')[0].get('id') # ID da mensagem recebida
            image = None

            # Verificar se o destinatário já existe
            # Atualizar ou criar o destinatário
            destinatario, _ = Destinatario.objects.update_or_create(
                    numero_telefone=numero_destinatario,
                    defaults={
                        'whatsapp_id': wa_id,
                        'nome_destinatario': name,
                    }
            )

            try:
                conversa = Conversa.objects.get(identificador_conversa=f"conversa_{wa_id}", status_room='novo', canal='whatsapp')
                # Se a conversa existe, verifique o status
                if conversa.status_room == 'novo':

                    conn = Conn_Whatsapp()
                    get_image_data = conn.image_get(id_image)

                    if get_image_data is not None:
                        
                        try:
                            # Salva o arquivo temporário no campo file_message
                            files_msg = Files_WhatsApp_Message.objects.create(
                                file_type=get_image_data['mime_type'],
                                file_size=get_image_data['file_size'],
                                file_id_whatsapp=get_image_data['file_id_whatsapp'],
                                file_message= get_image_data['file_message'],
                            )

                            print("Sucesso ao salvar a imagem!")
                        except IntegrityError as e:
                            print(f'ERRO ao Salvar: {e}')
                            return None

                        Mensagem.objects.create(
                            conversa=conversa,
                            conteudo=caption,
                            tipo='recebida',
                            data_hora_message=formated_timestamp,
                            wa_id_message= id_mensagem,
                            files=files_msg
                        )
            except Conversa.DoesNotExist:
                # Se a conversa não existir, crie um novo registro
                conversa = Conversa(identificador_conversa=f"conversa_{wa_id}", usuario=None, destinatario=destinatario, status_room='Novo', canal='whatsapp')
                conversa.save()
          
            # Enviar mensagem para o WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'conversa_{wa_id}',  # Nome do grupo WebSocket
                {
                    'type': 'chat_image',
                    'type_conteudo': 'image',
                    'image': get_image_data['file_message'],
                    'numerotelefone' : numero_destinatario,
                    'hora_back': timestamp.strftime("%H:%M"),
                    'type_arq': get_image_data['mime_type'],
                }
            )
        except Exception as e:
            print(e)
            traceback_str = traceback.format_exc()
            print(f"Erro: {traceback_str}")
        return image

    def alerts(self):
        alert_status = self.payload.get('alert_status')
        alert_description = self.payload.get('alert_description')
        return alert_status, alert_description
    
    def error_whatsapp(self):
        code = self.payload.get('code')
        title = self.payload.get('title')
        error_message = self.payload.get('message')
        error_data  = self.payload.get('error_data')
        details  = self.payload.get('details')
        return code, title, error_message, error_data, details
    
    def status_messages(self):
        wa_id = self.payload.get('statuses')[0].get('recipient_id') #ID do cliente no Whatsapp (Número de Telefone)
        id_mensagem_enviada = self.payload.get('statuses')[0].get('id')
        status = self.payload.get('statuses')[0].get('status')

        if self.payload.get('statuses')[0].get('status') == 'failed':
            error = self.payload.get('statuses')[0].get('errors')
            erro = json.dumps({
                'code': error[0].get('code'),
                'title': error[0].get('title'),
                'details': error[0].get('error_data').get('details'),
            })
        else:
            erro = None

        try:
            msg = Mensagem.objects.get(wa_id_message=id_mensagem_enviada)
            msg.status_message = status
            msg.save()
        except ObjectDoesNotExist:
            msg = Mensagem.objects.filter(wa_id_message=id_mensagem_enviada)
            for mensagem in msg:
                mensagem.status_message = status
                mensagem.save()

        # Enviar mensagem para o WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'conversa_{wa_id}',  # Nome do grupo WebSocket
            {
                'type': 'statuses',
                'type_conteudo': 'statuses',
                'status': status,
                'wa_id_message': id_mensagem_enviada,
                'error': erro 
            }
        )
        return status