# Generated by Django 4.2.2 on 2023-10-16 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payment', '0006_rename_procucts_payments_products'),
    ]

    operations = [
        migrations.AddField(
            model_name='payments',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
