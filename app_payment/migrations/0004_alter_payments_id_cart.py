# Generated by Django 4.2.2 on 2023-10-16 04:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_cart', '0002_itemcarrinho_valor_unitário'),
        ('app_payment', '0003_remove_payments_products_id_payments_id_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payments',
            name='id_cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ecommerce_cart.carrinho'),
        ),
    ]
