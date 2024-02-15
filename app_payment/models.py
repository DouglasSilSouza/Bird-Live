from unittest.util import _MAX_LENGTH
from django.db import models
from app_authentication.models import Cadastro

# Create your models here.
class Payments(models.Model):
    id_payment = models.IntegerField(unique=True, blank=False) #Id da cobrança (ou charge_id) / Ou loc para PIX
    txid_pix = models.CharField(max_length=40, null=True, blank=True, unique=True)
    user = models.ForeignKey(Cadastro, on_delete=models.DO_NOTHING) #Model do Usuario
    products = models.JSONField(null=True, blank=True) # JSON dos prodtudos
    date_created = models.DateTimeField(null=True, blank=True) # Data da Criação da Cobrança
    date_approved = models.DateTimeField(null=True, blank=True) # Data de Aprovação (Quando Aprovado)
    date_last_updated = models.DateTimeField(null=True, blank=True) # Data da Ultima Atualização
    status_payment = models.CharField(max_length=20) # Forma de Pagamento
    status_detail = models.CharField(max_length=100 ,null=True, blank=True) # Detalhes do Pagamento
    payment_type_id = models.CharField(max_length=15, null=True, blank=True) #Tipo de pagamento
    interest_free_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Valor Total sem juros
    interest_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Valor total com juros
    installments = models.IntegerField(null=True, blank=True) #Parcelas
    installments_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) #Valor das Parcelas

    def date_createdBR(self):
        return self.date_created.strftime('%d/%m/%Y %H:%M:%S')
    
    def date_approvedBR(self):
        return self.date_approved.strftime('%d/%m/%Y %H:%M:%S')

    def date_last_updatedBR(self):
        return self.date_last_updated.strftime('%d/%m/%Y %H:%M:%S')
    
    class Meta:
        db_table = 'payments'
        unique_together = ('id_payment', 'txid_pix')
    
    def __str__(self) -> str:
        return str(self.id_payment)




