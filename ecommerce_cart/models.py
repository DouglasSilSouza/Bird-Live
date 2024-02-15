# models.py

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from app_authentication.models import Cadastro
from decimal import Decimal

class Carrinho(models.Model):
    usuario = models.ForeignKey(Cadastro, on_delete=models.CASCADE, related_name='carrinho')
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'e-cart'
    
    def __str__(self) -> str:
        return self.usuario.first_name

    def enviar_payment(self):
        return self.itens.aggregate(total=models.Sum('subtotal'))['total'] or 0
    
    def get_itens(self):
        itens = self.itens.all()

        products = []

        for item in itens:
            products.append({
                "product_id": item.produto_id,
                "quantity": item.quantidade,
                "title": item.title,
                "valor_unitario": float((item.valor_unitario).quantize(Decimal('1.00'))),
                "subtotal": float((item.subtotal).quantize(Decimal('1.00'))),
                "image_url": item.image_url
            })
        return products

@receiver(post_save, sender='ecommerce_cart.ItemCarrinho')
@receiver(post_delete, sender='ecommerce_cart.ItemCarrinho')
def update_cart_total(sender, instance, **kwargs):
    carrinho = instance.carrinho
    carrinho.total = carrinho.itens.aggregate(total=models.Sum('subtotal'))['total'] or 0
    carrinho.save()

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto_id = models.PositiveIntegerField()
    title = models.TextField()
    description = models.TextField()
    image_url = models.TextField()
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'e-itemcarrinho'
    
    def __str__(self) -> str:
        return str(self.produto_id)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)
