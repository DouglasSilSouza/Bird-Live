from django.conf import settings
from django.db import models

class Destinatario(models.Model):
    whatsapp_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    telegram_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    numero_telefone_whatsapp = models.CharField(max_length=20, unique=True, null=True, blank=True)
    numero_telefone_telegram = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nome_destinatario = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'destinatario'
    
    def __str__(self) -> str:
        return self.nome_destinatario

class Conversa(models.Model):

    CANAIS_CHOICES = (
        ('wh', 'WhatsApp'),
        ('tl', 'Telegram'),
    )

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    destinatario = models.ForeignKey(Destinatario, on_delete=models.CASCADE)
    identificador_conversa = models.CharField(max_length=100)
    data_conversa = models.DateTimeField(auto_now_add=True)
    status_room = models.CharField(max_length=50, null=False, blank=False)
    canal = models.CharField(choices=CANAIS_CHOICES, max_length=20)

    def formatar_data_conversa(self):
        return self.data_conversa.strftime("%d/%m/%Y %H:%M:%S")

    class Meta:
        db_table = 'conversa'
    
    def __str__(self) -> str:
        return self.identificador_conversa

class Files_WhatsApp_Message(models.Model):
    file_message = models.TextField()
    file_type = models.CharField(max_length=20, null=True, blank=True)
    file_size = models.CharField(max_length=100, null=True, blank=True)
    file_id_whatsapp = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'arquivos_mensagens'
    
    def __str__(self) -> str:
        return self.file_message

class Mensagem(models.Model):
    TIPO_CHOICES = (
        ('recebida', 'Recebida'),
        ('enviada', 'Enviada'),
        ('modelo', 'Modelo'),
        ('finalizado', 'Finalizado'),
    )
    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE)
    conteudo = models.TextField(null=True, blank=True)
    data_hora_message = models.DateTimeField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    wa_id_message = models.CharField(max_length=100, unique=True, null=True)
    status_message = models.CharField(max_length=10, null=True, blank=True)
    files = models.ForeignKey(Files_WhatsApp_Message, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        db_table = 'mensagens'
        ordering = ['data_hora_message']
    
    def __str__(self) -> str:
        return self.conversa
    