from app_authentication.models import Cadastro
from django.db import models

# Create your models here.
class Carrinho(models.Model):
    usuario = models.ForeignKey(Cadastro, on_delete=models.CASCADE)

    class Meta:
        db_table = 'e-cart'
    
    def __str__(self) -> str:
        return self.usuario.first_name
    
    def calcular_total(self):
        total = 0
        itens = ItemCarrinho.objects.filter(carrinho=self)

        for item in itens:
            total += item.subtotal

        return total
    
    def get_itens(self):
        itens = ItemCarrinho.objects.filter(carrinho=self)

        products = []

        for item in itens:
            products.append({"product_id": item.produto_id, "quantity": item.quantidade, "title": item.title, "valor_unitario": item.valor_unitario, "subtotal": item.subtotal, "image_url": item.image_url})
        return products

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    produto_id = models.PositiveIntegerField()
    title = models.TextField()
    description = models.TextField()
    image_url = models.TextField()
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'e-itemcarrinho'
    
    def __str__(self) -> str:
        return self.produto_id
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)

