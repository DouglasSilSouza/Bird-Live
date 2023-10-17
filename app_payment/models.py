from django.db import models
from app_authentication.models import Cadastro

# Create your models here.
class Payments(models.Model):
    id_payment = models.IntegerField(50)
    user = models.ForeignKey(Cadastro, on_delete=models.DO_NOTHING)
    products = models.JSONField(null=True, blank=True)
    date_created = models.DateTimeField()
    date_approved = models.DateTimeField(null=True, blank=True)
    date_last_updated = models.DateTimeField()
    status_payment = models.CharField(max_length=20)
    status_detail = models.CharField(max_length=100)
    payment_type_id = models.CharField(max_length=15) #Tipo de pagamento
    payment_method_id = models.CharField(max_length=10, null=True, blank=True) #Bandeira do Cartão
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    installments = models.IntegerField()

    def date_createdBR(self):
        return self.date_created.strftime('%d/%m/%Y %H:%M:%S')
    
    def date_approvedBR(self):
        return self.date_approved.strftime('%d/%m/%Y %H:%M:%S')

    def date_last_updatedBR(self):
        return self.date_last_updated.strftime('%d/%m/%Y %H:%M:%S')
    
    class Meta:
        db_table = 'payments'
    
    def __str__(self) -> str:
        return self.id_payment




